from typing import Type, Optional
from .trait_interpreter import TraitInterpreter
from ..trait_assembler.stable_diffusion import TraitAssembler, StableDiffusionTraitAssembler


class StableDiffusionKeywordTraitInterpreter(TraitInterpreter):
    """
    Passthrough interpreter intended to work with StableDiffusionAssembler.
    """

    def interpret(self, trait_value: str, feature_properties: dict) -> Optional[dict]:
        if 'substitutes' not in feature_properties:
            raise KeyError(f'Config of this feature is not compatible with this interpreter!')

        return {
            'word': trait_value,
            'substitutes': feature_properties['substitutes']
        }
