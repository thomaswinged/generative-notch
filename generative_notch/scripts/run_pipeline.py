import argparse
from pprint import pprint
import os
from generative_notch import get_config, init_logger
from generative_notch.pipeline.pipeline import Pipeline
from generative_notch.pipeline.table_loader.csv import CSVTableLoader
from generative_notch.pipeline.table_loader.google_sheets import GoogleSheetsTableLoader
from generative_notch.pipeline.table_preprocessor.rescale_target_weights import NormalizeWeightsTablePreprocessor
from generative_notch.pipeline.combination_generator.target_weight_based import TargetWeightBasedCombinationGenerator
from generative_notch.pipeline.trait_interpreter.notch_property import NotchPropertyTraitInterpreter
from generative_notch.pipeline.trait_interpreter.notch_range_property import NotchRangePropertyInterpreter
from generative_notch.pipeline.trait_interpreter.stable_diffusion_keyword import StableDiffusionKeywordTraitInterpreter
from generative_notch.pipeline.trait_assembler.notch import NotchTraitAssembler
from generative_notch.pipeline.trait_assembler.stable_diffusion import StableDiffusionTraitAssembler
from generative_notch.pipeline.renderer.stable_diffusion import StableDiffusionRenderer
from generative_notch.pipeline.renderer.notch import NotchRenderer


init_logger()

parser = argparse.ArgumentParser()
parser.add_argument('config')
parser.add_argument('-count', '--n', dest='count', type=int)
# args = parser.parse_args()
# For testing purposes in order to debug in IDE
args = parser.parse_args([r'D:\git\generative_notch\generative_notch\config\config.yml', '--n', '200'])
# TODO Handle various config files

config = get_config(args.config)


result = (
    Pipeline()
    # .tableLoader.set(
    #     GoogleSheetsTableLoader(
    #         google_sheets_config=config['google_sheets']
    #     )
    # )
    # .tablePreprocessor.register(
    #     NormalizeWeightsTablePreprocessor(
    #         table_config=config['table']
    #     )
    # )
    # .combinationGenerator.set(
    #     TargetWeightBasedCombinationGenerator(
    #         n=args.count,
    #         save_filepath=config['output_dir'],
    #         table_config=config['table']
    #     )
    # )
    .tableLoader.set(
        CSVTableLoader(
            filepath=r'D:\git\generative_notch\tests\data\combinations.csv'
        )
    )
    # .traitInterpreter.register(
    #     NotchPropertyTraitInterpreter(
    #         compatible_assembler=NotchTraitAssembler,
    #         compatible_keyword='set_single_notch_property',
    #         config=config['feature']
    #     )
    # )
    # .traitInterpreter.register(
    #     NotchRangePropertyInterpreter(
    #         compatible_assembler=NotchTraitAssembler,
    #         compatible_keyword='set_single_notch_property_in_range',
    #         config=config['feature']
    #     )
    # )
    .traitInterpreter.register(
        StableDiffusionKeywordTraitInterpreter(
            compatible_assembler=StableDiffusionTraitAssembler,
            compatible_keyword='substitute_stable_diffusion_keyword',
            config=config['feature']
        )
    )
    .traitAssembler.register(
        StableDiffusionTraitAssembler(
            compatible_renderer=StableDiffusionRenderer,
            config=config
        )
    )
    # .traitAssembler.register(
    #     NotchTraitAssembler(
    #         compatible_renderer=NotchRenderer,
    #         config=config
    #     ).add_instruction_manually({
    #         'node': '$F_SubjectPhoto',
    #         'property': 'Attribute.Image Path',
    #         'value': os.path.join(
    #             config['stable_diffusion']['save_dir'],
    #             'SubjectPhoto_{batch_name}_{combination_id}.png'
    #         )
    #     })
    # )
    .renderer.register(
        StableDiffusionRenderer()
    )
    # .renderer.register(
    #     NotchRenderer()
    # )
    # .outputPostprocessor.register(
    #     LoopOutputPostprocessor(
    #         ffmpeg_path=config['ffmpeg'],
    #         duration_seconds=config['render_settings']['duration_frames'] / config['render_settings'][
    #             'fps'],
    #         target_size=config['render_settings']['target_size_kb'],
    #         replace_original=True
    #     )
    # )
    # .outputPostprocessor.register(
    #     ConvertToH264OutputPostprocessor(
    #         ffmpeg_path=config['ffmpeg'],
    #         duration_frames=config['render_settings']['duration_frames'],
    #         loop_frames=config['render_settings']['loop_frames'],
    #         fps=config['render_settings']['fps'],
    #         replace_original=True
    #     )
    # )
    # .finalizer.register(
    #     ShowContainingDirectoriesFinalizer()
    # )
    .run()
)

pprint(result, width=200)
