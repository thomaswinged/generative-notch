from typing import Type
from random import randrange
from .trait_interpreter import TraitInterpreter
from ..trait_assembler.notch import TraitAssembler, NotchTraitAssembler


class NotchRangePropertyInterpreter(TraitInterpreter):
    """
    Passthrough interpreter intended to work with NotchAssembler.

    Range is written in form of "x-y" string.
    Sample data that this interpreter expects from config:
    {
        node: $F_Text
        property: Attribute, Text
    }
    """

    def get_compatible_assembler(self) -> Type[TraitAssembler]:
        return NotchTraitAssembler

    def interpret(self, trait_value: str, feature_properties: dict) -> dict:
        start, stop = trait_value.split('-')
        drawn = randrange(int(start), int(stop), 1)

        return {
            'node': feature_properties['node'],
            'property': feature_properties['property'],
            'value': str(drawn)
        }
