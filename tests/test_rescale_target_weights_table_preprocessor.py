import unittest
from generative_notch import get_config
from io import StringIO
import pandas as pd
from generative_notch.pipeline.table_preprocessor.rescale_target_weights import NormalizeWeightsTablePreprocessor

DEBUG_INPUT = 'feature_name,trait_name,target_weight\r\nA,aa,1.0\r\nA,aaa,11.0\r\nB,bb,2.0\r\nB,bbb,22.0\r\nC,cc,3.0\r\nC,ccc,33.0\r\n'
CORRECT_RESULT = 'feature_name,trait_name,target_weight\r\nA,aa,0.08333333333333333\r\nA,aaa,0.9166666666666666\r\nB,bb,0.08333333333333333\r\nB,bbb,0.9166666666666666\r\nC,cc,0.08333333333333333\r\nC,ccc,0.9166666666666666\r\n'
CONFIG = {
    'feature_column_name': 'feature_name',
    'trait_column_name': 'trait_name',
    'weights_column_name': 'target_weight'
}

class TestRescaleTargetWeightsTablePreprocessor(unittest.TestCase):
    def test_set_up(self):
        result = NormalizeWeightsTablePreprocessor(
            table_config=CONFIG
        )
        self.assertIsInstance(result, NormalizeWeightsTablePreprocessor)

    def test_run(self):
        table = pd.read_csv(StringIO(DEBUG_INPUT), sep=',', index_col=0)
        result = NormalizeWeightsTablePreprocessor(
            table_config=CONFIG
        ).run(table)

        self.assertEqual(result.to_csv(), CORRECT_RESULT)


if __name__ == '__main__':
    unittest.main()
