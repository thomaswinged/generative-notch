from .trait_interpreter import TraitInterpreter


class StableDiffusionKeywordTraitInterpreter(TraitInterpreter):
    """
    Passthrough interpreter intended to work with StableDiffusionAssembler.
    """
    def interpret(self, trait_value: str, feature_properties: dict) -> dict:
        return {
            'word': trait_value,
            'substitutes': feature_properties['substitutes']
        }
