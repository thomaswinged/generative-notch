import logging
import gspread
import pandas as pd
from attrs import define
from gspread_dataframe import get_as_dataframe
from .table_loader import TableLoader


@define
class GoogleSheetsTableLoader(TableLoader):
    """
    Google Sheet data loader
    """

    google_sheets_config: dict

    def run(self) -> pd.DataFrame:
        logging.info(f'Loading Google Sheets data...')

        df = load_table_from_google_sheets(
            credentials_filename=self.google_sheets_config['credentials'],
            sheet_filename=self.google_sheets_config['sheet'],
            worksheet_name=self.google_sheets_config['worksheet']
        )

        return (
            df
            .dropna(axis=0, how='all').dropna(axis=1, how='all')
            .ffill()
        )


def load_table_from_google_sheets(credentials_filename: str, sheet_filename: str, worksheet_name: str) -> pd.DataFrame:
    gc = gspread.service_account(filename=credentials_filename)
    sh = gc.open(sheet_filename)
    worksheet = sh.worksheet(worksheet_name)

    return get_as_dataframe(worksheet)
