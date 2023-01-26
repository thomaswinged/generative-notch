import logging
from typing import Type, Tuple, Optional
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

    :param compatible_keyword: keyword that interpreter looks for when reading config to determine which features should it process
    :param compatible_assembler: TraitAssembler that this interpreter interprets information for
    :param config: a dictionary from which interpreter reads feature properties
    :param assembly_instructions: a collection of interpreted traits gather when `run` is called, prepared for assembly
    """
    config: dict = field(validator=instance_of(dict))
    @config.validator
    def __config_validator(self, _, val: dict):
        if not val.keys():
            raise ValueError(f'Provided config does not have any keys!')

    compatible_keyword: str
    compatible_assembler: Type[TraitAssembler]
    assembly_instructions: list[dict] = field(factory=list, init=False)

    def run(self, feature_name: str, trait_value: str) -> None:
        """
        :param feature_name: name of a feature, needs to match the provided config
        :param trait_value: value of a trait: needs to match the provided config
        """
        if feature_name not in self.config:
            raise ValueError(f'Given feature [{feature_name}] does not exist in provided config!')
        elif 'action' not in self.config[feature_name]:
            raise KeyError(f'Ill-formed feature config - it needs to implement [action] key with compatible keyword!')
        elif self.config[feature_name]['action'] != self.compatible_keyword:
            logging.warning(f'This interpreter does not implement [{self.compatible_keyword}] action keyword!')
            return

        if instruction := self.interpret(trait_value, self.config[feature_name]):
            self.assembly_instructions.append(instruction)

    @abstractmethod
    def interpret(self, trait_value: str, feature_properties: dict) -> Optional[dict]:
        """
        Defines a method of interpreting the trait. Should not be executed manually, use `run()` instead.
        Return assembly instruction, e.g.:
        {
            'node': '$F_MyText',
            'property': Attributes.Text,
            'value': 'Hello World!'
        }
        The return is optional as it's possible for the derived interpreter to gather more traits before it can make an output

        :param trait_value: value of a trait
        :param feature_properties: a collection of feature properties, that should be used to interpret the trait value
        :return: optional, a single assembly instruction
        """
        pass

    def get_result(self) -> Tuple[Type['TraitAssembler'], list[dict]]:
        """
        Returns all instructions for compatible assembler gathered via interpreting provided traits.
        :return: compatible assembler and matching instructions
        """

        return self.compatible_assembler, self.assembly_instructions
