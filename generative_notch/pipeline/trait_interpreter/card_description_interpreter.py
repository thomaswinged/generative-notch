from attrs import define, field
import logging
from typing import Type, Optional
from collections import defaultdict
from .trait_interpreter import TraitInterpreter
from ..trait_assembler.notch import TraitAssembler, NotchTraitAssembler


@define
class CardDescriptionTraitInterpreter(TraitInterpreter):
    _stencil: dict = field(init=False)

    def __attrs_post_init__(self):
        self._stencil = defaultdict(str)

    def _is_ready_for_output(self) -> bool:
        return self._stencil['profession'] and self._stencil['clan']

    def interpret(self, trait_value: str, feature_properties: dict) -> Optional[dict]:
        if 'substitutes' not in feature_properties:
            raise KeyError(f'Config of this feature is not compatible with this interpreter!')

        self._stencil[feature_properties['substitutes']] = trait_value

        if self._is_ready_for_output():
            return {
                'node': '$F_Description',
                'property': 'Attributes, Text String',
                'value': f"{self._stencil['profession']} {self._stencil['clan']}"
            }