from attrs import define
from typing import Type
from abc import ABC, abstractmethod

RenderInstructions = dict[Type['Renderer'], list[dict]]


@define
class Renderer(ABC):
    config: dict

    @abstractmethod
    def run(self, render_instructions: list[dict]) -> list[str]:
        pass
