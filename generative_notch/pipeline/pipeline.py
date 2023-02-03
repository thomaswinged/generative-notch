from typing import Type
import logging
import pandas as pd
from collections import defaultdict
from attrs import define, field
from .table_loader.table_loader import TableLoader
from .table_preprocessor.table_preprocessor import TablePreprocessor
from .combination_generator.combination_generator import CombinationGenerator
from .trait_interpreter.trait_interpreter import TraitInterpreter
from .trait_assembler.trait_assembler import TraitAssembler, AssemblyInstructions
from .renderer.renderer import Renderer, RenderInstructions


class NotRegistered(Exception):
    pass


@define
class TableLoaderPipelineModule:
    pipeline: 'Pipeline'
    loader: TableLoader = field(init=False)

    def run(self) -> pd.DataFrame:
        try:
            result = self.loader.run()
            return result
        except AttributeError:
            raise NotRegistered(f'TableLoader has not beet set!')

    def set(self, loader: TableLoader) -> 'Pipeline':
        logging.debug(f'Setting TableLoader: {loader}')
        self.loader = loader
        return self.pipeline


@define
class TablePreprocessorPipelineModule:
    pipeline: 'Pipeline'
    preprocessors: list[TablePreprocessor] = field(init=False, factory=list)

    def run(self, table: pd.DataFrame) -> pd.DataFrame:
        result = table.copy()

        for preprocessor in self.preprocessors:
            result = preprocessor.run(result)

        return result

    def register(self, preprocessor: TablePreprocessor) -> 'Pipeline':
        logging.debug(f'Registering TablePreprocessor: {preprocessor}')
        self.preprocessors.append(preprocessor)
        return self.pipeline


@define
class CombinationGeneratorPipelineModule:
    pipeline: 'Pipeline'
    generator: CombinationGenerator = field(init=False)

    def run(self, table: pd.DataFrame) -> pd.DataFrame:
        if not hasattr(self, 'generator'):
            logging.warning('CombinationGenerator has not been set! Assuming that the table contains combinations.')
            return table

        result = self.generator.run(table)
        return result

    def set(self, generator: CombinationGenerator) -> 'Pipeline':
        logging.debug(f'Setting CombinationGenerator: {generator}')
        self.generator = generator
        return self.pipeline


@define
class TraitInterpreterPipelineModule:
    pipeline: 'Pipeline'
    interpreters: list[TraitInterpreter] = field(init=False, factory=list)

    def run(self, combinations: pd.DataFrame) -> dict[int, AssemblyInstructions]:
        result: dict[int, AssemblyInstructions] = {}

        for idx, combination in combinations.iterrows():
            combination_id = int(str(idx))
            result[combination_id] = {}

            for interpreter in self.interpreters:
                for feature, trait in combination.items():
                    interpreter.run(str(feature), trait)

                assembler_type, instructions = interpreter.get_result()

                if assembler_type not in result[combination_id]:
                    result[combination_id][assembler_type]: list[dict] = []

                result[combination_id][assembler_type].extend(instructions)
                instructions.clear()

        return result

    def register(self, interpreter: TraitInterpreter) -> 'Pipeline':
        logging.debug(f'Registering TraitInterpreter: {interpreter}')
        self.interpreters.append(interpreter)
        return self.pipeline


@define
class TraitAssemblerPipelineModule:
    pipeline: 'Pipeline'
    assemblers: dict[Type[TraitAssembler], TraitAssembler] = field(init=False, factory=dict)

    def run(self, indexed_assembly_instructions: dict[int, AssemblyInstructions]) -> dict[int, RenderInstructions]:
        result: dict[int, RenderInstructions] = {}

        # Assert that all required assemblers has been registered
        # TODO Move into a function that will be triggered in validation stage
        for combination_id, assembly_instructions in indexed_assembly_instructions.items():
            for assembler_type, instructions in assembly_instructions.items():
                if assembler_type not in self.assemblers:
                    raise NotRegistered(f'Required TraitAssembler [{assembler_type}] is not registered')

        # Perform actual assembling
        for combination_id, assembly_instructions in indexed_assembly_instructions.items():
            result[combination_id] = {}

            for assembler_type, instructions in assembly_instructions.items():
                assembler = self.assemblers[assembler_type]

                renderer_type, partial_instructions = assembler.run(
                        assembly_instructions=instructions,
                        context={
                            'combination_id': combination_id
                        }
                )

                if renderer_type not in result[combination_id]:
                    result[combination_id][renderer_type]: list[dict] = []

                result[combination_id][renderer_type].extend(partial_instructions)

        return result

    def register(self, assembler: TraitAssembler) -> 'Pipeline':
        logging.debug(f'Registering TraitAssembler: {assembler}')
        self.assemblers[type(assembler)] = assembler
        return self.pipeline


@define
class RendererPipelineModule:
    pipeline: 'Pipeline'
    renderers: dict[Type[Renderer], Renderer] = field(init=False, factory=dict)

    def run(self, indexed_render_instructions: dict[int, RenderInstructions]) -> list[str]:
        # Check if all required Renderers are registered
        # TODO Move into a function that will be triggered in validation stage
        for combination_id, render_instructions in indexed_render_instructions.items():
            for renderer_type in render_instructions.keys():
                if renderer_type not in self.renderers:
                    raise NotRegistered(f'Required Renderer [{renderer_type}] is not registered!')

        # Perform actual rendering
        result: list[str] = []
        for combination_id, render_instructions in indexed_render_instructions:
            for renderer_type, instruction in render_instructions:
                renderer = self.renderers[renderer_type]
                output_filepaths = renderer.run(instruction)
                result.extend(output_filepaths)

        return result

    def register(self, renderer: Renderer) -> 'Pipeline':
        logging.debug(f'Registering Renderer: {renderer}')
        self.renderers[type(renderer)] = renderer
        return self.pipeline


class Pipeline:
    def __init__(self):
        self.tableLoader = TableLoaderPipelineModule(self)
        self.tablePreprocessor = TablePreprocessorPipelineModule(self)
        self.combinationGenerator = CombinationGeneratorPipelineModule(self)
        self.traitInterpreter = TraitInterpreterPipelineModule(self)
        self.traitAssembler = TraitAssemblerPipelineModule(self)
        self.renderer = RendererPipelineModule(self)
        self.outputPostprocessor = None
        self.finalizer = None

    def run(self):
        table = self.tableLoader.run()
        preprocessed_table = self.tablePreprocessor.run(table)
        combinations = self.combinationGenerator.run(preprocessed_table)
        assembly_instructions = self.traitInterpreter.run(combinations)
        render_instructions = self.traitAssembler.run(assembly_instructions)
        output_footage = self.renderer.run(render_instructions)

        return output_footage
        # postprocessed_footage: list[str] = self.outputPostprocessor.run(output_footage)
        # feedback: str = self.finalizer.run(postprocessed_footage)

        # return feedback
