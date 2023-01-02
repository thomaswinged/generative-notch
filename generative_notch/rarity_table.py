import logging
import os.path
import pandas as pd
import numpy as np
import gspread
from gspread_dataframe import get_as_dataframe
from itertools import product
from tqdm import tqdm
import seaborn as sns
from io import StringIO


class RarityTable:
	def __init__(self, raw_data: pd.DataFrame):
		self.__raw_data = raw_data
		self.__feature_names = list(self.__raw_data['feature_name'].unique())
		self.__possible_combinations = self.__generate_possible_combinations()
		self.__combinations_left_to_sample = self.__possible_combinations.copy()
		self.__weights = pd.DataFrame()
		self.__combinations = pd.DataFrame()

	def __repr__(self):
		return self.raw_data.to_string()

	@property
	def raw_data(self) -> pd.DataFrame:
		"""
		:returns: loaded raw data
		"""
		return self.__raw_data.copy()

	@property
	def feature_names(self) -> list[str]:
		"""
		:returns: list of feature names (first column of Google Sheet data)
		"""
		return self.__feature_names.copy()

	@property
	def possible_combinations(self) -> pd.DataFrame:
		"""
		:returns: product table of all traits per feature
		"""
		return self.__possible_combinations.copy()

	def __generate_possible_combinations(self) -> pd.DataFrame:
		"""Generates all possible combinations using cartesian product
		:returns: product table of all traits per feature
		"""
		traits_per_feature = []
		for trait, sub_df in self.__raw_data.groupby('feature_name', sort=False):
			traits_per_feature.append(sub_df['trait_name'].values)

		return pd.DataFrame(list(product(*traits_per_feature)), columns=self.feature_names)

	@property
	def max_combinations(self) -> int:
		"""
		:returns: max count of possible to generate combinations
		"""
		return len(self.__possible_combinations)

	@property
	def weights_frame(self) -> pd.DataFrame:
		"""Generate combinations first to update weights table
		:returns: frame containing target and current weights of each trait
		"""
		if self.__weights.empty:
			raise AssertionError('Generate combinations first!')

		return self.__weights.copy()

	@property
	def combinations(self) -> pd.DataFrame:
		"""Need to generate combinations before calling this property
		:returns: generated combinations
		"""
		if self.__combinations.empty:
			raise AssertionError('Generate combinations first!')

		return self.__combinations.copy()

	@classmethod
	def from_google_sheets(cls, credentials_filename: str, sheet_filename: str, worksheet_name: str) -> 'RarityTable':
		"""Loads data from Google Sheet and creates RarityTable using that data
		Source of implementation: https://codesolid.com/google-sheets-in-python-and-pandas/

		:param credentials_filename: path to json file containing credentials allowing access to Google Sheets
		:param sheet_filename: Name of a sheet file, f.e. MyRarityTable
		:param worksheet_name: name of a worksheet inside sheet, f.e. Sheet1
		:returns: created RarityTable
		"""
		logging.info(f'Loading Google Sheets data...')
		gc = gspread.service_account(filename=credentials_filename)
		sh = gc.open(sheet_filename)
		worksheet = sh.worksheet(worksheet_name)

		df = (
			get_as_dataframe(worksheet, usecols=[0, 1, 2])
            .dropna(how='all')
            .assign(feature_name=lambda d: d['feature_name'].ffill())
		)

		# Re-scale target_weights to range 0:1
		df = (
			df
			.assign(
				target_weight=lambda d: d
                .groupby('feature_name')
				['target_weight']
                .apply(lambda x: x / x.sum())
			)
		)

		logging.debug(f'Done')
		return cls(df)

	@classmethod
	def from_dummy_data(cls) -> 'RarityTable':
		"""Debug function for creating RarityTable from debug data
		:returns: created RarityTable
		"""
		logging.info(f'Loading data...')
		dummy_data = """feature_name;trait_name;target_weight
			0;Block1;Cobble;0.7692307692307693
			1;Block1;Gold;0.07692307692307693
			2;Block1;Silver;0.15384615384615385
			3;Block2;Bronze;0.2
			4;Block2;Clay;0.6
			5;Block2;None;0.2
			6;Block3;Rock;0.7142857142857143
			7;Block3;Rubber;0.07142857142857142
			8;Block3;Steel;0.21428571428571427
			"""
		df = pd.read_csv(StringIO(dummy_data.replace('\t', '')), sep=';')

		logging.debug(f'Done')
		return cls(df)

	def generate_combinations(self, n: int = -1) -> pd.DataFrame:
		"""Given target number of combinations generates combinations fitting loaded rarity table
		When n is equal to -1, will generate all possible combinations
		:returns: generated combinations
		"""

		if n == -1:
			count = self.max_combinations
		elif n > self.max_combinations:
			raise ValueError(f'Cannot generate {n} combinations, possible count is {self.max_combinations}')
		else:
			count = n

		self.__combinations = pd.DataFrame(columns=self.feature_names)
		self.__combinations_left_to_sample = self.__possible_combinations.copy()
		self.__weights = self.__create_weights_frame()

		for _ in tqdm(range(count), desc='Generating combinations'):
			combination_proposition = self.__get_next_combination()
			self.__combinations = pd.concat([self.__combinations, combination_proposition], ignore_index=True)
			self.__update_weights_frame()

		logging.debug(f'Done')
		return self.combinations

	def __create_weights_frame(self) -> pd.DataFrame:
		"""
		Based on the loaded data, creates a DataFrame with additional columns containing weights info.
		Weights table is being used to calculate necessity of sampling specific traits.
		:returns: frame containing weights
		"""
		result = (
			self.__raw_data
            .set_index(['feature_name', 'trait_name'])
            .assign(current_weight=lambda d: np.zeros_like(d.target_weight))
            .assign(weight_difference=lambda d: d.target_weight - d.current_weight)
		)

		return result

	def __get_next_combination(self) -> pd.DataFrame:
		"""
		Uses the rarity weights frame to calculate current distribution difference weight for every not sampled combination
		:returns: combination with the largest distribution difference (keeps most adequate distribution of traits)
		"""
		best_match_idx = (
			self.__combinations_left_to_sample
            .stack()
            .reset_index()
            .set_axis(['index', 'feature_name', 'trait_name'], axis=1)
            .merge(
				(
					self.__weights
					.reset_index()
					[['feature_name', 'trait_name', 'weight_difference']]
				),
				on=['feature_name', 'trait_name'],
				how='left'
			)
            .set_index(['index', 'feature_name'])
            .unstack()
            .assign(cumulative_weights_difference=lambda d: d.loc[:, 'weight_difference'].sum(axis=1))
            .drop('weight_difference', axis=1)
            .pipe(lambda d: d.set_axis(d.columns.droplevel(0), axis=1))
            .pipe(lambda d: d.set_axis([*d.columns[:-1], 'cumulative_weights_difference'], axis=1, inplace=False))
            .nlargest(1, columns='cumulative_weights_difference')
            .index
		)

		best_match = self.__combinations_left_to_sample.iloc[best_match_idx, :]
		self.__combinations_left_to_sample = (
			self.__combinations_left_to_sample
            .drop(index=best_match_idx)
            .reset_index(drop=True)
		)

		return best_match

	def __update_weights_frame(self):
		"""
		Updates weights frame
		"""
		# Update traits current distribution
		for feature in self.feature_names:
			distribution = self.__combinations[feature].value_counts(normalize=True)
			for trait in self.__combinations[feature].unique():
				self.__weights.at[(feature, trait), 'current_weight'] = distribution[trait]

		# Update traits weights difference
		self.__weights = (
			self.__weights
			.assign(weight_difference=lambda d: d.target_weight - d.current_weight)
		)

	def plot_rarity_distribution_error(self, n_point: int = 10, plot_average: bool = False):
		"""
		Plots distribution error of rarity sampling.
		Too big value of n_points will produce artifacts in plot.
		"""
		result = pd.DataFrame()
		for i in range(n_point):
			curr_range = (0, (i + 1) / n_point)
			series = (
				self.weights_frame_by_range(curr_range[0], curr_range[1])
                .reset_index()
                .assign(weight_difference=lambda d: abs(d['weight_difference']))
                .groupby('feature_name')
                .median()
				['weight_difference']
                .rename(curr_range)
			)
			result = pd.concat([result, series], axis=1)

		result = (
			result
            .T
            .assign(index=np.linspace(0, len(self.combinations), n_point))
		)

		if plot_average:
			result = (
				result
				.assign(AVERAGE=lambda d: d.median(axis=1))
				[['index', 'AVERAGE']]
			)

		result = (
			result
            .melt(id_vars='index')
            .set_axis(['combinations count', 'feature', 'distribution error [%]'], axis=1)
		)

		sns.lmplot(data=result, x='combinations count', y='distribution error [%]', hue='feature', ci=None, order=3, truncate=True)

	def weights_frame_by_range(self, start: float, end: float) -> pd.DataFrame:
		"""
		Creates weights table for specified range of combinations table (0.0 - 1.0)
		"""
		result = self.__create_weights_frame()
		combinations_slice = self.combinations_by_range(start, end)

		for feature in self.feature_names:
			distribution = combinations_slice[feature].value_counts(normalize=True)
			for trait in combinations_slice[feature].unique():
				result.at[(feature, trait), 'current_weight'] = distribution[trait]

		# Update traits weights difference
		result = (
			result
			.assign(weight_difference=lambda d: d.target_weight - d.current_weight)
		)
		return result

	def combinations_by_range(self, start: float,  end: float) -> pd.DataFrame:
		"""
		Returns slice of generated combinations based on provided percentage (0.0 - 1.0)
		"""
		return self.__combinations.iloc[int(len(self.__combinations) * start): int(len(self.__combinations) * end), :]

	def save(self, filename, directory):
		os.makedirs(directory, exist_ok=True)
		filepath = os.path.join(directory, filename) + '.json'
		with open(filepath, 'w') as output:
			output.write(self.combinations.T.to_json(indent=4))
