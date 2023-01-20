from .trait_interpreter import TraitInterpreter


class NotchPropertyTraitInterpreter(TraitInterpreter):
    def run(self, feature_name: str, trait_name: str):
        node = self._get_properties(feature_name)['node']
        props = self._get_properties(feature_name)['property']
        value = self._get_properties(feature_name)['options'][trait_name]

        self._add_instruction({
            'node': node,
            'property': props,
            'value': value
        })
