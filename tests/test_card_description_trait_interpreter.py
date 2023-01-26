import unittest
from generative_notch.pipeline.trait_interpreter.card_description_interpreter import CardDescriptionTraitInterpreter
from generative_notch.pipeline.trait_assembler.notch import NotchTraitAssembler

CONFIG = {
    'Clan': {
        'action': 'substitute_stable_diffusion_keyword',
        'substitutes': 'clan'
    },
    'Profession': {
        'action': 'substitute_stable_diffusion_keyword',
        'substitutes': 'profession'
    },
    'Random': {
        'action': 'substitute_stable_diffusion_keyword',
        'substitutes': 'random'
    }
}


class TestCardDescriptionTraitInterpreter(unittest.TestCase):
    def test_is_ready(self):
        interpreter = CardDescriptionTraitInterpreter(
            compatible_assembler=NotchTraitAssembler,
            compatible_keyword='substitute_stable_diffusion_keyword',
            config=CONFIG
        )
        interpreter._stencil['profession'] = 'viking'
        self.assertFalse(interpreter._is_ready_for_output())
        interpreter._stencil['random'] = 'qwerty'
        self.assertFalse(interpreter._is_ready_for_output())
        interpreter._stencil['clan'] = 'dwarf'
        self.assertTrue(interpreter._is_ready_for_output())

    def test_run(self):
        interpreter = CardDescriptionTraitInterpreter(
            compatible_assembler=NotchTraitAssembler,
            compatible_keyword='substitute_stable_diffusion_keyword',
            config=CONFIG
        )
        interpreter.run('Clan', 'dwarf')
        result = interpreter.get_result()
        self.assertEqual(
            result,
            (
                NotchTraitAssembler,
                []
            )
        )

        interpreter.run('Random', 'qwerty')
        result = interpreter.get_result()
        self.assertEqual(
            result,
            (
                NotchTraitAssembler,
                []
            )
        )

        interpreter.run('Profession', 'hunter')
        result = interpreter.get_result()
        self.assertEqual(
            result,
            (
                NotchTraitAssembler,
                [{
                    'node': '$F_Description',
                    'property': 'Attributes, Text String',
                    'value': 'hunter dwarf'
                }]
            )
        )


if __name__ == '__main__':
    unittest.main()
