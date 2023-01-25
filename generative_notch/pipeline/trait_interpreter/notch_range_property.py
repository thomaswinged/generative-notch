import logging
from typing import Type
from random import randint
from re import search
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
        if m := search(r'([0-9]*)\s*-\s*([0-9]*)(?:\s*,\s*([0-9]*.?[0-9]*))?', trait_value):
            start, stop, step = float(m.group(1)), float(m.group(2)), m.group(3)
            step = float(step) if step else 1.0
            drawn = randrange_float(start, stop, float(step))

            if not drawn % 1:  # not sure if this is needed, but I will try it
                drawn = int(drawn)

            return {
                'node': feature_properties['node'],
                'property': feature_properties['property'],
                'value': str(drawn)
            }
        else:
            raise ValueError(f'Range should constructed as follows: <min>-<max>,<step:optional>')


def randrange_float(start, stop, step=1.0):
    return randint(0, int((stop - start) / step)) * step + start
