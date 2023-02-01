import unittest
from generative_notch.pipeline.trait_assembler.stable_diffusion import StableDiffusionTraitAssembler
from generative_notch.pipeline.renderer.stable_diffusion import StableDiffusionRenderer


INSTRUCTIONS = [
    {
        'word': 'Thomas',
        'substitutes': 'name'
    }, {
        'word': 'staring in the stars',
        'substitutes': 'activity'
    }
]

CONFIG = {
    'stable_diffusion': {
        'prompt': "My name is {name} and I am currently {activity}."
    }
}

CORRECT_INTERPOLATION = "My name is Thomas and I am currently staring in the stars."


class TestStableDiffusionTraitAssembler(unittest.TestCase):
    def test_run(self):
        assembler = StableDiffusionTraitAssembler(
            compatible_renderer=StableDiffusionRenderer,
            config=CONFIG
        )
        result = assembler.run(INSTRUCTIONS)

        self.assertEqual(
            result,
            (
                StableDiffusionRenderer,
                [{
                    'prompt': CORRECT_INTERPOLATION
                }]
            )
        )


if __name__ == '__main__':
    unittest.main()
