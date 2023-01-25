import logging
import unittest
from generative_notch.pipeline.trait_interpreter.notch_range_property import NotchRangePropertyInterpreter, NotchTraitAssembler

CONFIG = {
    'MyFeature': {
        'action': 'my_action_keyword',
        'node': '$F_MyNode',
        'property': 'Attributes, Value'
    }
}


class TestNotchRangePropertyInterpreter(unittest.TestCase):
    def test_simple_run(self):
        interpreter = NotchRangePropertyInterpreter(
            action='my_action_keyword',
            config=CONFIG
        )
        interpreter.run('MyFeature', '5-6,0.5')
        result = interpreter.get_result()

        self.assertGreaterEqual(
            float(result[1][0]['value']), 5
        )
        self.assertLessEqual(
            float(result[1][0]['value']), 6
        )

    def test_not_digit_range(self):
        with self.assertRaises(ValueError):
            interpreter = NotchRangePropertyInterpreter(
                action='my_action_keyword',
                config=CONFIG
            )
            interpreter.run('MyFeature', 'not_a_range')


if __name__ == '__main__':
    unittest.main()
