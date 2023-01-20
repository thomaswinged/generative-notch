from .trait_assembler import TraitAssembler, AssemblyInstructions
from ..renderer.renderer import RenderInstructions


class StableDiffusionTraitAssembler(TraitAssembler):
    def run(self, additional_context: dict, assembly_instructions: list[dict]) -> RenderInstructions:
        interpolated_instructions = self.interpolate_instructions(additional_context, assembly_instructions)

        replacements = {}
        for instruction in interpolated_instructions:
            replacements.update(instruction)

        prompt = interpolate_prompt(
            prompt=self.config['stable_diffusion']['prompt'],
            dictionary=replacements
        )

        render_instructions = [{
            'prompt': prompt
        }]

        return {
            self.compatible_renderer: render_instructions
        }


def interpolate_prompt(prompt: str, dictionary: dict):
    return prompt.format(**dictionary)


# save_directory=config['stable_diffusion']['save_dir']