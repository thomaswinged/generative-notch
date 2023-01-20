from generative_notch import get_config
from generative_notch.dfx.dfx import Dfx
from pandas import Series, DataFrame
import logging
import itertools
from tqdm import tqdm
from math import ceil


class CombinationAssembler:
	def __init__(self, template_project_filepath: str):
		self.filepath = template_project_filepath
		self.dfx = Dfx(template_project_filepath)
		self.cfg = get_config()

	def __repr__(self):
		return f'CombinationAssembler("{self.filepath}")'

	def assemble(self, combinations: DataFrame, out_project_dir: str, out_project_name: str, out_video_dir: str) -> dict[str, list]:
		"""Using all available project layers, assemble given combinations.
		Will create files with suffix {combination_no_start}_{combination_no_end}

		:param combinations: combinations to assemble
		:param out_project_dir: directory in which will save assembled .dfx files
		:param out_project_name: base name for .dfx file
		:param out_video_dir: directory that the render queue will render videos to
		:returns: dictionary {dfx_filepath: list of filepaths of videos to render}
		"""
		logging.info(f"\nAssembling combination DFX combination projects to: {out_project_dir}")

		result = {}

		layers_count = len(self.dfx.script.layers)
		assembled = 0

		for _ in tqdm(range(ceil(len(combinations) / layers_count)), desc='Assembling combination projects'):
			start = assembled
			project_outputs = []
			for i, comb in enumerate(itertools.islice(combinations.iterrows(), assembled, assembled + layers_count)):
				out_video_name = f'{out_project_name}_{assembled}'
				project_outputs.append(
					self.__assemble_single(comb[1], i, out_video_dir, out_video_name)
				)
				assembled += 1

			dfx_out_name = out_project_name + f'-{start}_{assembled}'
			project_filepath = self.dfx.save(out_project_dir, dfx_out_name, True)
			result[project_filepath] = project_outputs
			self.dfx.reset(True)

		logging.debug('Done assembling!')
		return result

	def __assemble_single(self, combination: Series, layer_id: int, out_video_dir: str, out_video_name: str) -> str:
		"""Assembled single combination using a given layer

		:param combination: combination to assemble
		:param layer_id: layer to use
		:param out_video_dir: directory that the render queue will render videos to
		:param out_video_name: name of a video that will be rendered by render queue
		:returns: filepath to file where layer will be rendered to
		"""
		logging.debug(f"Assembling single combination: {combination.to_dict()} in layer {layer_id}")

		layer = self.dfx.script.layer(layer_id)
		for feature, trait in combination.items():
			node = self.cfg['feature'][feature]['node']

			for prop, value in self.cfg['feature'][feature]['trait'][trait].items():
				prop = tuple(prop.split(', '))
				layer.node(node).property(*prop).set(value)

		result = self.dfx.script.render_queue._add_instruction(layer, out_video_dir, out_video_name)
		return result
