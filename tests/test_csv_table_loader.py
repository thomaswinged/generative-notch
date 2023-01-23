import unittest
import pandas as pd
from pandas.testing import assert_frame_equal
from generative_notch.pipeline.table_loader.csv import CSVTableLoader


CSV_FILEPATH = r'D:\git\generative_notch\tests\data\debug_data.csv'


class TestCSVTableLoader(unittest.TestCase):
    def test_set_up(self):
        result = CSVTableLoader(
            filepath=CSV_FILEPATH
        )
        self.assertIsInstance(result, CSVTableLoader)

    def test_invalid_path(self):
        with self.assertRaises(FileNotFoundError):
            result = CSVTableLoader(
                filepath='not_existing_file.csv'
            )

    def test_run(self):
        table = CSVTableLoader(
            filepath=CSV_FILEPATH
        ).run()

        assert_frame_equal(
            table,
            pd.read_csv(CSV_FILEPATH)
        )


if __name__ == '__main__':
    unittest.main()
