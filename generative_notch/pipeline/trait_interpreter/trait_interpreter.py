from typing import Type
from abc import ABC, abstractmethod
from attrs import define, field
from attrs.validators import optional, instance_of
from ..trait_assembler.trait_assembler import TraitAssembler, AssemblyInstructions


@define
class TraitInterpreter(ABC):
    """
    Given feature properties and trait to decrypt, prepares assembly instructions.

    :param action: keyword that interpreter looks for
    :param config: a dictionary from which interpreter reads feature properties
    :param compatible_assembler: can be specified during instantiation of interpreter or inside derived class
    :param assembly_instructions: a collection of interpreted traits, prepared for assembly
    """
    action: str
    config: dict
    compatible_assembler: TraitAssembler = field(default=None, validator=optional(instance_of(Type[TraitAssembler])))
    assembly_instructions: list[dict] = field(factory=list, init=False)

    def run(self, feature_name: str, trait_value: str) -> None:
        """
        :param feature_name: name of a feature, needs to match the provided config
        :param trait_value: value of a trait: needs to match the provided config
        """
        if self.config['feature'][feature_name]['action'] != self.action:
            return

        instruction = self.interpret(
            trait_value,
            self.config['feature'][feature_name]
        )

        self.assembly_instructions.append(instruction)

    @abstractmethod
    def interpret(self, trait_value: str, feature_properties: dict) -> dict:
        """
        The only method that derived classes needs to override.
        Return assembly instruction, e.g.:
        {
            'node': '$F_MyText',
            'property': Attributes.Text,
            'value': 'Hello World!'
        }

        :param trait_value: value of a trait
        :param feature_properties: a collection of feature properties, that should be used to interpret the trait value
        :return: a single assembly instruction
        """
        pass

    def get_result(self) -> AssemblyInstructions:
        """
        Returns all instructions for compatible assembler gathered via interpreting provided traits.
        :return: assembly instructions
        """
        if not self.compatible_assembler:
            raise ValueError(f'Compatible interpreter not specified!')

        return {
            self.compatible_assembler: self.assembly_instructions
        }
