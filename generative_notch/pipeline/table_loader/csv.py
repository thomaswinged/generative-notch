from attrs import define, field
import os
import pandas as pd
from .table_loader import TableLoader


@define
class CSVTableLoader(TableLoader):
    """
    Loads data from CSV file.
    """
    filepath: str = field()
    @filepath.validator
    def __filepath_validator(self, attr, val):
        if not os.path.exists(val):
            raise FileNotFoundError(f'CSV filepath {val} is not valid!')

    def run(self) -> pd.DataFrame:
        result = pd.read_csv(self.filepath)
        return result
