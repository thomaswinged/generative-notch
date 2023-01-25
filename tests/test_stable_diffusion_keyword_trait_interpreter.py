import unittest
from generative_notch.pipeline.trait_interpreter.stable_diffusion_keyword import StableDiffusionKeywordTraitInterpreter, StableDiffusionTraitAssembler

CONFIG = {
    'MyFeature': {
        'action': 'my_action_keyword',
        'substitutes': 'subs'
    }
}


class TestStableDiffusionKeywordTraitInterpreter(unittest.TestCase):
    def test_simple_run(self):
        interpreter = StableDiffusionKeywordTraitInterpreter(
            action='my_action_keyword',
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


if __name__ == '__main__':
    unittest.main()
