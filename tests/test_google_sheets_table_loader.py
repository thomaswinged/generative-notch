import unittest
from generative_notch import get_config
from generative_notch.pipeline.table_loader import GoogleSheetsTableLoader


CORRECT_RESULT = 'feature_name,trait_name,target_weight\r\nA,aa,1.0\r\nA,aaa,11.0\r\nB,bb,2.0\r\nB,bbb,22.0\r\nC,cc,3.0\r\nC,ccc,33.0\r\n'


class GoogleSheetsTableLoaderTestCase(unittest.TestCase):
    def test_set_up(self):
        GoogleSheetsTableLoader(
            credentials_filename=get_config()['google_sheets']['credentials'],
            sheet_filename=get_config()['google_sheets']['sheet'],
            worksheet_name='DEBUG'
        )

    def test_run(self):
        table = GoogleSheetsTableLoader(
            credentials_filename=get_config()['google_sheets']['credentials'],
            sheet_filename=get_config()['google_sheets']['sheet'],
            worksheet_name='DEBUG'
        ).run()

        self.assertEqual(table.to_csv(index=None), CORRECT_RESULT)


if __name__ == '__main__':
    unittest.main()
