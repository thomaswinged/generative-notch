import logging
from typing import Type, Tuple
from abc import ABC, abstractmethod
from attrs import define, field
from attrs.validators import instance_of
from ..trait_assembler.trait_assembler import TraitAssembler


@define
class TraitInterpreter(ABC):
    """
    Given feature properties and trait to decrypt, prepares assembly instructions.
    A basic input config dict should be constructed this way:
    {
        <feature_name> {
            action: <my_action_keyword>
            ... feature-dependent params ...
        }
        <feature_name> {
            action: <my_action_keyword>
            ... feature-dependent params ...
        }
    }

    :param action: keyword that interpreter looks for when reading config to determine which features should it process
    :param config: a dictionary from which interpreter reads feature properties
    :param assembly_instructions: a collection of interpreted traits gather when `run` is called, prepared for assembly
    """
    action: str
    config: dict = field(validator=instance_of(dict))
    @config.validator
    def __config_validator(self, attr, val:dict):
        if not val.keys():
            raise ValueError(f'Provided config does not have any keys!')
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
        if feature_name not in self.config:
            raise ValueError(f'Given feature [{feature_name}] does not exist in provided config!')
        elif self.config[feature_name]['action'] != self.action:
            logging.warning(f'This interpreter does not implement [{self.action}] action keyword!')
            return

        instruction = self.interpret(
            trait_value,
            self.config[feature_name]
        )

        self.assembly_instructions.append(instruction)

    @abstractmethod
    def interpret(self, trait_value: str, feature_properties: dict) -> dict:
        """
        Defines a method of interpreting the trait. Should not be executed manually, use `run()` instead.
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
