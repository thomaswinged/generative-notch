from attrs import define, field
from string import Formatter
from re import findall
from typing import Type
from abc import ABC, abstractmethod
from flatten_dict import flatten
from flatten_dict.reducers import make_reducer
from ..renderer.renderer import Renderer, RenderInstructions

AssemblyInstructions = dict[Type['TraitAssembler'], list[dict]]


@define
class TraitAssembler(ABC):
    """
    Generates intermediate assets and project files.

    :param __extra_instructions: list of dictionary containing instructions for assembling
    :return: Renderer to be used and list of instructions that are enough to perform the render, e.g. filepaths
    """
    compatible_renderer: Type[Renderer]
    config: dict
    __extra_instructions: list[dict] = field(factory=list, init=False)

    def run(self, assembly_instructions: list[dict], context: dict) -> RenderInstructions:
        # extend context by whole config
        flat_cfg = flatten_dict(self.config)
        extended_context = dict(context, **flat_cfg)

        interpolated_instructions = interpolate_instructions(
            instructions=assembly_instructions + self.__extra_instructions,
            context=extended_context
        )

        output_instruction = self.assemble(interpolated_instructions)

        return {
            self.compatible_renderer: output_instruction
        }

    @abstractmethod
    def assemble(self, assembly_instructions: list[dict]) -> list[dict]:
        pass

    def add_instruction_manually(self, instruction: dict) -> 'TraitAssembler':
        """
        Manually append an instruction to input assembly instructions list.
        """
        self.__extra_instructions.append(instruction)
        return self


def flatten_dict(dictionary: dict, reducer: str = '.'):
    return flatten(dictionary, reducer=make_reducer(reducer))


def interpolate_instructions(instructions: list[dict], context: dict) -> list[dict]:
    """
    Interpolate instruction using given config and additional context.
    e.g. 'value': 'SubjectPhoto_{batch_name}_{render_settings.width}.png'
    """
    result: list[dict] = []

    for instruction in instructions:
        result.append(
            interpolate_single_instruction(instruction, context)
        )
    return result


class __InstructionFormatter(Formatter):
    """
    I had to create this formatter in order to format string that requires usage of dot in attr name, e.g.:
    >>> p = 'resolution={render.width}x{render.height}.png'
    >>> c = {'render.width': '1920', 'render.height': '1080'}
    >>> r = ['render.width', 'render.height']
    >>> p.format(**c)
    KeyError: 'render'
    """
    def get_field(self, field_name, args, kwargs):
        return self.get_value(field_name, args, kwargs), field_name


def interpolate_single_instruction(instruction: dict, context: dict) -> dict:
    result = {}

    for key, value in instruction.items():
        required_keys = findall('{(.+?)}', value)
        try:
            tailored_context = {key: context[key] for key in required_keys}
            result[key] = __InstructionFormatter().vformat(value, [], tailored_context)
        except KeyError:
            raise KeyError(f'Instruction {[value]} requires interpolation, the context is insufficient: {context}')

    return result
