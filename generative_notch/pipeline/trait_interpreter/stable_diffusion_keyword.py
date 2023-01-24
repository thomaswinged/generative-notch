from typing import Type
from .trait_interpreter import TraitInterpreter
from ..trait_assembler.stable_diffusion import TraitAssembler, StableDiffusionTraitAssembler


class StableDiffusionKeywordTraitInterpreter(TraitInterpreter):
    """
    Passthrough interpreter intended to work with StableDiffusionAssembler.
    """

    def get_compatible_assembler(self) -> Type[TraitAssembler]:
        return StableDiffusionTraitAssembler

    def interpret(self, trait_value: str, feature_properties: dict) -> dict:
        return {
            'word': trait_value,
            'substitutes': feature_properties['substitutes']
        }
