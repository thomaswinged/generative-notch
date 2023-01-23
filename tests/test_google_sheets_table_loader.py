import unittest
from generative_notch.pipeline.table_loader.google_sheets import GoogleSheetsTableLoader


CORRECT_RESULT = 'feature_name,trait_name,target_weight\r\nA,aa,1.0\r\nA,aaa,11.0\r\nB,bb,2.0\r\nB,bbb,22.0\r\nC,cc,3.0\r\nC,ccc,33.0\r\n'
CONFIG = {
    'credentials': 'D:\git\generative_notch\generative_notch\config\google_sheets_credentials.json',
    'sheet': 'generative_notch-rarity_table',
    'worksheet': 'DEBUG'
}


class TestGoogleSheetsTableLoader(unittest.TestCase):
    def test_set_up(self):
        result = GoogleSheetsTableLoader(
            google_sheets_config=CONFIG
        )
        self.assertIsInstance(result, GoogleSheetsTableLoader)

    def test_run(self):
        table = GoogleSheetsTableLoader(
            google_sheets_config=CONFIG
        ).run()

        self.assertEqual(table.to_csv(index=False), CORRECT_RESULT)


if __name__ == '__main__':
    unittest.main()
