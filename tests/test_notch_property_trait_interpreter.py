import logging
import unittest
from generative_notch.pipeline.trait_interpreter.notch_property import NotchPropertyTraitInterpreter, NotchTraitAssembler

CONFIG = {
    'MyFeature': {
        'action': 'my_action_keyword',
        'node': '$F_MyNode',
        'property': 'Attributes, Value',
        'options': {
            'Opt1': 0.25,
            'Opt2': 0.5,
            'Opt3': 1
        }
    }
}


class TestNotchPropertyTraitInterpreter(unittest.TestCase):
    def test_simple_run(self):
        interpreter = NotchPropertyTraitInterpreter(
            action='my_action_keyword',
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
                action='my_action_keyword',
                config={}
            )

    def test_not_existing_action(self):
        with self.assertLogs(level=logging.WARNING):
            interpreter = NotchPropertyTraitInterpreter(
                action='non_existing_action',
                config=CONFIG
            )
            interpreter.run('MyFeature', 'Opt2')

    def test_not_existing_feature(self):
        with self.assertRaises(ValueError):
            interpreter = NotchPropertyTraitInterpreter(
                action='my_action_keyword',
                config=CONFIG
            )
            interpreter.run('NotExistingFeature', 'Opt2')

    def test_not_existing_option(self):
        with self.assertRaises(ValueError):
            interpreter = NotchPropertyTraitInterpreter(
                action='my_action_keyword',
                config=CONFIG
            )
            interpreter.run('MyFeature', 'NotExistingOption')


if __name__ == '__main__':
    unittest.main()
