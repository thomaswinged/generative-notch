from .trait_assembler import TraitAssembler, AssemblyInstructions
from ..renderer.renderer import RenderInstructions


class StableDiffusionTraitAssembler(TraitAssembler):
    def assemble(self, assembly_instructions: list[dict]) -> list[dict]:
        substitutions = {}
        for instruction in assembly_instructions:
            substitutions.update(instruction)

        prompt = self.config['stable_diffusion']['prompt'].format(**substitutions)

        return [{
            'prompt': prompt
        }]
