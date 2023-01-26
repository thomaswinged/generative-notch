import logging
import unittest
from generative_notch.pipeline.trait_interpreter.notch_property import NotchPropertyTraitInterpreter, NotchTraitAssembler

CONFIG = {
    'MyFeature': {
        'action': 'set_single_notch_property',
        'node': '$F_MyNode',
        'property': 'Attributes, Value',
        'options': {
            'Opt1': 0.25,
            'Opt2': 0.5,
            'Opt3': 1
        }
    }
}

INVALID_CONFIG = {
    'MyFeature': {
        'action': 'set_single_notch_property',
        'node_name': '$F_MyNode',
        'prop': 'Attributes, Value',
        'opt': {
            'Opt1': 0.25,
            'Opt2': 0.5,
            'Opt3': 1
        }
    }
}


class TestNotchPropertyTraitInterpreter(unittest.TestCase):
    def test_run(self):
        interpreter = NotchPropertyTraitInterpreter(
            compatible_assembler=NotchTraitAssembler,
            compatible_keyword='set_single_notch_property',
            config=CONFIG
        )
        interpreter.run('MyFeature', 'Opt2')
        result = interpreter.get_result()

        self.assertEqual(
            result,
            (
                NotchTraitAssembler,
                [{
                    'node': '$F_MyNode',
                    'property': 'Attributes, Value',
                    'value': 0.5
                }]
            )
        )

    def test_empty_config(self):
        with self.assertRaises(ValueError):
            NotchPropertyTraitInterpreter(
                compatible_assembler=NotchTraitAssembler,
                compatible_keyword='set_single_notch_property',
                config={}
            )

    def test_not_existing_feature(self):
        with self.assertRaises(ValueError):
            interpreter = NotchPropertyTraitInterpreter(
                compatible_assembler=NotchTraitAssembler,
                compatible_keyword='set_single_notch_property',
                config=CONFIG
            )
            interpreter.run('NotExistingFeature', 'Opt2')

    def test_not_existing_option(self):
        with self.assertRaises(ValueError):
            interpreter = NotchPropertyTraitInterpreter(
                compatible_assembler=NotchTraitAssembler,
                compatible_keyword='set_single_notch_property',
                config=CONFIG
            )
            interpreter.run('MyFeature', 'NotExistingOption')

    def test_illformed_config_action(self):
        with self.assertRaises(KeyError):
            interpreter = NotchPropertyTraitInterpreter(
                compatible_assembler=NotchTraitAssembler,
                compatible_keyword='set_single_notch_property',
                config={
                    'MyFeature': {
                        'actn': 'set_single_notch_property'
                    }
                }
            )
            interpreter.run('MyFeature', 'my_word')

    def test_illformed_config(self):
        with self.assertRaises(KeyError):
            interpreter = NotchPropertyTraitInterpreter(
                compatible_assembler=NotchTraitAssembler,
                compatible_keyword='set_single_notch_property',
                config=INVALID_CONFIG
            )
            interpreter.run('MyFeature', 'Opt2')

    def test_no_compatible_keyword(self):
        with self.assertLogs(level=logging.WARNING):
            interpreter = NotchPropertyTraitInterpreter(
                compatible_assembler=NotchTraitAssembler,
                compatible_keyword='non_existing_action',
                config=CONFIG
            )
            interpreter.run('MyFeature', 'Opt2')


if __name__ == '__main__':
    unittest.main()
