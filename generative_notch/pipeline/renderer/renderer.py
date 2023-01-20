from typing import Type
from abc import ABC, abstractmethod

RenderInstructions = dict[Type['Renderer'], list[dict]]


class Renderer(ABC):
    @abstractmethod
    def run(self, render_instructions: list[dict]) -> list[str]:
        pass
