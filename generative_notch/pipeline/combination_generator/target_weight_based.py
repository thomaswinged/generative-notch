import logging
from attrs import define
from itertools import product
from tqdm import tqdm
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from .combination_generator import CombinationGenerator


@define
class TargetWeightBasedCombinationGenerator(CombinationGenerator):
    """
    Generates combinations fitting distribution specified in the given  rarity table.
    When n is equal to -1, will generate all possible combinations.
    """

    table_config: dict

    def run(self, rarity_table: pd.DataFrame) -> pd.DataFrame:
        possible_combinations = generate_possible_combinations(
            rarity_table=rarity_table,
            feature_column_name=self.table_config['feature_column_name'],
            trait_column_name=self.table_config['trait_column_name']
        )
        max_combinations = len(possible_combinations)

        count = max_combinations if self.n == -1 else self.n
        if count > max_combinations:
            raise ValueError(f'Cannot generate {count} combinations, possible count is {max_combinations}')

        result = pd.DataFrame(columns=rarity_table[self.table_config['feature_column_name']].unique().tolist())
        combinations_left_to_sample = possible_combinations.copy()
        distribution_table = construct_distribution_table(
            rarity_table=rarity_table,
            feature_column_name=self.table_config['feature_column_name'],
            trait_column_name=self.table_config['trait_column_name'],
            weights_column_name=self.table_config['weights_column_name']
        )

        for _ in tqdm(range(count), desc='Generating combinations'):
            best_matching_combination, remaining_combinations = extract_next_combination(
                combinations=combinations_left_to_sample,
                distribution_table=distribution_table,
                feature_column_name=self.table_config['feature_column_name'],
                trait_column_name=self.table_config['trait_column_name']
            )
            combinations_left_to_sample = remaining_combinations
            result = pd.concat([result, best_matching_combination], ignore_index=True)
            distribution_table = update_distribution_table(
                distribution_table=distribution_table,
                combinations=result
            )

        logging.debug(f'Done')

        plot_distribution_error(
            distribution_table=distribution_table,
            combinations=result
        )

        return result

    def save(self):
        pass


def generate_possible_combinations(
        rarity_table: pd.DataFrame,
        feature_column_name: str, trait_column_name: str
) -> pd.DataFrame:
    """Generates all possible combinations using cartesian product
    :returns: product table of all traits per feature
    """
    traits_per_feature = []
    for trait, sub_df in rarity_table.groupby(feature_column_name, sort=False):
        traits_per_feature.append(sub_df[trait_column_name].values)

    return pd.DataFrame(
        list(product(*traits_per_feature)),
        columns=rarity_table['feature_name'].unique()
    )


def construct_distribution_table(
        rarity_table: pd.DataFrame, feature_column_name: str, trait_column_name: str, weights_column_name: str
) -> pd.DataFrame:
    """
    Based on given rarity table, creates a DataFrame containing current and target weights per feature.
    Distribution table is being used to calculate necessity of sampling specific traits.
    :returns: frame containing current and target weights per feature
    """
    return (
        rarity_table
        .set_index([feature_column_name, trait_column_name])
        .assign(current_weight=lambda d: np.zeros_like(d[weights_column_name]))
        .assign(weight_difference=lambda d: d.target_weight - d.current_weight)
    )


def extract_next_combination(
        combinations: pd.DataFrame, distribution_table: pd.DataFrame,
        feature_column_name: str, trait_column_name: str
) -> tuple[pd.Series, pd.DataFrame]:
    """
    Uses the rarity weights frame to calculate current distribution difference weight for every not sampled combination
    :returns: combination with the largest distribution difference (keeps most adequate distribution of traits)
    """
    best_match_idx = (
        combinations
        .stack()
        .reset_index()
        .set_axis(['index', feature_column_name, trait_column_name], axis=1)
        .merge(
            (
                distribution_table
                .reset_index()
                [[feature_column_name, trait_column_name, 'weight_difference']]
            ),
            on=[feature_column_name, trait_column_name],
            how='left'
        )
        .set_index(['index', feature_column_name])
        .unstack()
        .assign(cumulative_weights_difference=lambda d: d.loc[:, 'weight_difference'].sum(axis=1))
        .drop('weight_difference', axis=1)
        .pipe(lambda d: d.set_axis(d.columns.droplevel(0), axis=1))
        .pipe(lambda d: d.set_axis([*d.columns[:-1], 'cumulative_weights_difference'], axis=1, inplace=False))
        .nlargest(1, columns='cumulative_weights_difference')
        .index
    )

    best_match = combinations.iloc[best_match_idx, :]
    remaining_combinations = (
        combinations
        .drop(index=best_match_idx)
        .reset_index(drop=True)
    )

    return best_match, remaining_combinations


def update_distribution_table(
        distribution_table: pd.DataFrame, combinations: pd.DataFrame
) -> pd.DataFrame:
    """
    Updates weights frame
    """
    result = distribution_table.copy()

    # Update traits current distribution
    for feature in combinations.columns:
        distribution = combinations[feature].value_counts(normalize=True)
        for trait in combinations[feature].unique():
            result.at[(feature, trait), 'current_weight'] = distribution[trait]

    # Update traits weights difference
    return (
        result
        .assign(weight_difference=lambda d: d.target_weight - d.current_weight)
    )


def combinations_by_range(
        combinations: pd.DataFrame, start: float, end: float
) -> pd.DataFrame:
    """
    Returns slice of generated combinations based on provided percentage (0.0 - 1.0)
    """
    return combinations.iloc[int(len(combinations) * start): int(len(combinations) * end), :]


def weights_frame_by_range(
        distribution_table: pd.DataFrame, combinations: pd.DataFrame, start: float, end: float
) -> pd.DataFrame:
    """
    Creates weights table for specified range of combinations table (0.0 - 1.0)
    """
    result = distribution_table.copy()
    combinations_slice = combinations_by_range(combinations, start, end)

    for feature in combinations.columns:
        distribution = combinations_slice[feature].value_counts(normalize=True)
        for trait in combinations_slice[feature].unique():
            result.at[(feature, trait), 'current_weight'] = distribution[trait]

    # Update traits weights difference
    result = (
        result
        .assign(weight_difference=lambda d: d.target_weight - d.current_weight)
    )
    return result


def plot_distribution_error(
        distribution_table: pd.DataFrame, combinations: pd.DataFrame,
        n_point: int = 10, average: bool = False
) -> None:
    """
    Plots distribution error of rarity sampling.
    Too big value of n_points will produce artifacts in plot.
    """
    result = pd.DataFrame()

    for i in range(n_point):
        curr_range = (0, (i + 1) / n_point)
        series = (
            weights_frame_by_range(distribution_table, combinations, curr_range[0], curr_range[1])
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
        .assign(index=np.linspace(0, len(combinations), n_point))
    )

    if average:
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

    sns.lmplot(data=result, x='combinations count', y='distribution error [%]', hue='feature', ci=None, order=3,
               truncate=True)
    plt.show()
