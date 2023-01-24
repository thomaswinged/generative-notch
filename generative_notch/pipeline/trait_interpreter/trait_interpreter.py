from typing import Type, Tuple
from abc import ABC, abstractmethod
from attrs import define, field
from ..trait_assembler.trait_assembler import TraitAssembler


@define
class TraitInterpreter(ABC):
    """
    Given feature properties and trait to decrypt, prepares assembly instructions.

    :param action: keyword that interpreter looks for
    :param config: a dictionary from which interpreter reads feature properties
    :param assembly_instructions: a collection of interpreted traits, prepared for assembly
    """
    action: str
    config: dict
    assembly_instructions: list[dict] = field(factory=list, init=False)

    @abstractmethod
    def get_compatible_assembler(self) -> Type[TraitAssembler]:
        """
        Should return assembler type that is compatible with instructions interpreted by derived TraitInterpreter
        """
        pass

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
        Defines a method of interpreting the trait
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

    def get_result(self) -> Tuple[Type['TraitAssembler'], list[dict]]:
        """
        Returns all instructions for compatible assembler gathered via interpreting provided traits.
        :return: compatible assembler and matching instructions
        """
        if not self.get_compatible_assembler():
            raise ValueError(f'Compatible interpreter not specified!')

        return self.get_compatible_assembler(), self.assembly_instructions
