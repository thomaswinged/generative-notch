import unittest
import logging
from generative_notch.pipeline.trait_assembler.trait_assembler import flatten_dict, interpolate_instructions

CONFIG = {
    'batch_name': 'MyShinyBatch',
    'render': {
        'width': '1920',
        'height': '1080'
    }
}

CONTEXT = {
    'combination_id': '001'
}

INSTRUCTIONS = [
    {
        'node': '$F_MyImageLoader',
        'property': 'Attributes, File Source',
        'value': 'SubjectPhoto_{batch_name}_{combination_id}_{render.width}x{render.height}.png'
    }
]

CORRECTLY_INTERPOLATED = [
    {
        'node': '$F_MyImageLoader',
        'property': 'Attributes, File Source',
        'value': 'SubjectPhoto_MyShinyBatch_001_1920x1080.png'
    }
]


class TestStableDiffusionTraitAssembler(unittest.TestCase):
    def test_flatten_config(self):
        result = flatten_dict(
            dictionary=CONFIG,
            reducer='.'
        )
        self.assertEqual(
            result,
            {
                'batch_name': 'MyShinyBatch',
                'render.width': '1920',
                'render.height': '1080'
            }
        )

    def test_interpolate_instructions(self):
        flat_cfg = flatten_dict(CONFIG)
        extended_context = dict(CONTEXT, **flat_cfg)

        result = interpolate_instructions(INSTRUCTIONS, extended_context)
        self.assertEqual(
            result,
            CORRECTLY_INTERPOLATED
        )


if __name__ == '__main__':
    unittest.main()
