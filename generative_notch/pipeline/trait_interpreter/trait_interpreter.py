from typing import Type
from abc import ABC, abstractmethod
from attrs import define, field, validators
from ..trait_assembler.trait_assembler import TraitAssembler, AssemblyInstructions


@define
class TraitInterpreter(ABC):
    """
    Given feature properties and trait to decrypt, prepares assembly instructions.
    """
    action: str
    compatible_assembler: field(validator=validators.instance_of(Type[TraitAssembler]))
    config: dict
    assembly_instructions: list[dict] = field(factory=list, init=False)

    @abstractmethod
    def run(self, feature_name: str, trait_name: str) -> None:
        pass

    def get_result(self) -> AssemblyInstructions:
        return {
            self.compatible_assembler: self.assembly_instructions
        }

    def _get_properties(self, feature_name: str) -> dict:
        return self.config['feature'][feature_name]

    def _add_instruction(self, instruction: dict) -> 'TraitInterpreter':
        self.assembly_instructions.append(instruction)
        return self
