from .trait_interpreter import TraitInterpreter


class StableDiffusionKeywordTraitInterpreter(TraitInterpreter):
    def run(self, feature_name: str, trait_name: str):
        word = trait_name
        substitutes = self._get_properties(feature_name)['substitutes']

        self._add_instruction({
            word: word,
            substitutes: substitutes
        })
