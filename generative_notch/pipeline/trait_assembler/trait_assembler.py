from attrs import define, field
from typing import Type
from abc import ABC, abstractmethod
from flatten_dict import flatten
from flatten_dict.reducers import make_reducer
from ..renderer.renderer import Renderer, RenderInstructions

AssemblyInstructions = dict[Type['TraitAssembler'], list[dict]]


@define
class TraitAssembler(ABC):
    """

    """
    compatible_renderer: Type[Renderer]
    extra_instructions: list = field(factory=list, init=False)
    config: dict

    @abstractmethod
    def run(self, additional_context: dict, assembly_instructions: list[dict]) -> RenderInstructions:
        pass

    def add_extra_instruction(self, instruction: dict) -> 'TraitAssembler':
        """
        Add an instruction that will be appended to the output of this trait assembler.
        """
        self.extra_instructions.append(instruction)
        return self

    def interpolate_instructions(self, context: dict, assembly_instructions: list[dict]) -> list[dict]:
        """
        Interpolate instruction using given config and additional context.
        e.g. 'value': 'SubjectPhoto_{batch_name}_{render_settings.width}.png'
        """
        result: list[dict] = []
        flatten_cfg = flatten(self.config, reducer=make_reducer('.'))
        extended_context = dict(context, **flatten_cfg)

        for i, instruction in enumerate(assembly_instructions):
            result[i] = interpolate_instruction(
                instruction=instruction,
                context=extended_context
            )
        return result


def interpolate_instruction(instruction: dict, context: dict) -> dict:
    result = {}
    for key, value in instruction:
        result[key] = value.format(**context)

    return result
