import unittest
from generative_notch.pipeline.trait_interpreter.notch_range_property import NotchRangePropertyInterpreter, NotchTraitAssembler

CONFIG = {
    'MyFeature': {
        'action': 'set_single_notch_property_in_range',
        'node': '$F_MyNode',
        'property': 'Attributes, Value'
    }
}

INVALID_CONFIG = {
    'MyFeature': {
        'action': 'set_single_notch_property_in_range',
        'node_name': '$F_MyNode',
        'prop': 'Attributes, Value'
    }
}


class TestNotchRangePropertyInterpreter(unittest.TestCase):
    def test_result_assembler_type(self):
        interpreter = NotchRangePropertyInterpreter(
            compatible_assembler=NotchTraitAssembler,
            compatible_keyword='set_single_notch_property_in_range',
            config=CONFIG
        )
        interpreter.run('MyFeature', '5-6')
        result = interpreter.get_result()

        self.assertEqual(
            result[0], NotchTraitAssembler
        )

    def test_is_result_in_range(self):
        interpreter = NotchRangePropertyInterpreter(
            compatible_assembler=NotchTraitAssembler,
            compatible_keyword='set_single_notch_property_in_range',
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

    def test_illformed_config(self):
        with self.assertRaises(KeyError):
            interpreter = NotchRangePropertyInterpreter(
                compatible_assembler=NotchTraitAssembler,
                compatible_keyword='set_single_notch_property_in_range',
                config=INVALID_CONFIG
            )
            interpreter.run('MyFeature', '5-6,0.5')

    def test_not_digit_range(self):
        with self.assertRaises(ValueError):
            interpreter = NotchRangePropertyInterpreter(
                compatible_assembler=NotchTraitAssembler,
                compatible_keyword='set_single_notch_property_in_range',
                config=CONFIG
            )
            interpreter.run('MyFeature', 'not_a_range')


if __name__ == '__main__':
    unittest.main()
