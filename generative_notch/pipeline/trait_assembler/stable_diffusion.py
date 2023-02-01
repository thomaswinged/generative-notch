import logging

from .trait_assembler import TraitAssembler


class StableDiffusionTraitAssembler(TraitAssembler):
    def assemble(self, assembly_instructions: list[dict]) -> list[dict]:
        substitutions = {}
        for instruction in assembly_instructions:
            substitutions[instruction['substitutes']] = instruction['word']
        logging.warning(self.config['stable_diffusion']['prompt'])

        prompt = self.config['stable_diffusion']['prompt'].format(**substitutions)

        return [{
            'prompt': prompt + ', ' + self.config['stable_diffusion']['extra_prompt']
        }]
