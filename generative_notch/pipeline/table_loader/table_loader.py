from abc import ABC, abstractmethod
import pandas as pd


class TableLoader(ABC):
    """
    Loads data from any source and returns raw rarity table.
    """
    @abstractmethod
    def run(self) -> pd.DataFrame:
        pass
