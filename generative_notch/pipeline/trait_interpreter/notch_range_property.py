from random import randrange
from .trait_interpreter import TraitInterpreter


class NotchRangePropertyInterpreter(TraitInterpreter):
    """
    Range is written in form of "x-y" string.
    """
    def run(self, feature_name: str, trait_name: str):
        node = self._get_properties(feature_name)['node']
        props = self._get_properties(feature_name)['property']

        start, stop = trait_name.split('-')
        drawn = randrange(int(start), int(stop), 1)

        self._add_instruction({
            'node': node,
            'property': props,
            'value': str(drawn)
        })
