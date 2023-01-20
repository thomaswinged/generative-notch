from attrs import define
from .renderer import Renderer


class NotchRenderer(Renderer):
    def run(self, instructions: list[dict]) -> list[str]:
        pass
