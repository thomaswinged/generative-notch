import unittest
from generative_notch.pipeline.trait_interpreter.stable_diffusion_keyword import StableDiffusionKeywordTraitInterpreter, StableDiffusionTraitAssembler

CONFIG = {
    'MyFeature': {
        'action': 'substitute_stable_diffusion_keyword',
        'substitutes': 'subs'
    }
}

INVALID_CONFIG = {
    'MyFeature': {
        'action': 'substitute_stable_diffusion_keyword',
        'subs': 'subs'
    }
}


class TestStableDiffusionKeywordTraitInterpreter(unittest.TestCase):
    def test_run(self):
        interpreter = StableDiffusionKeywordTraitInterpreter(
            compatible_assembler=StableDiffusionTraitAssembler,
            compatible_keyword='substitute_stable_diffusion_keyword',
            config=CONFIG
        )
        interpreter.run('MyFeature', 'my_word')
        result = interpreter.get_result()

        self.assertEqual(
            result,
            (
                StableDiffusionTraitAssembler,
                [{
                    'word': 'my_word',
                    'substitutes': 'subs'
                }]
            )
        )

    def test_illformed_config(self):
        with self.assertRaises(KeyError):
            interpreter = StableDiffusionKeywordTraitInterpreter(
                compatible_assembler=StableDiffusionTraitAssembler,
                compatible_keyword='substitute_stable_diffusion_keyword',
                config=INVALID_CONFIG
            )
            interpreter.run('MyFeature', 'my_word')


if __name__ == '__main__':
    unittest.main()
