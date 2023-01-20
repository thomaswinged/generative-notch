from .trait_assembler import TraitAssembler
from ..renderer.renderer import RenderInstructions


class NotchTraitAssembler(TraitAssembler):
    def run(self, additional_context: dict, assembly_instructions: list[dict]) -> RenderInstructions:
        interpolated_instructions = self.interpolate_instructions(additional_context, assembly_instructions)

        for instruction in interpolated_instructions:
            print(instruction)


# template_project_filepath=config['dfx_template_file'],
# out_project_name=config['batch_name'],
# out_project_dir=config['dfx_intermediate_dir'],
# out_video_dir=config['output_dir']