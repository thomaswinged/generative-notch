from attrs import define
from .renderer import Renderer


class StableDiffusionRenderer(Renderer):
    def run(self, instructions: list[dict]) -> list[str]:
        pass
