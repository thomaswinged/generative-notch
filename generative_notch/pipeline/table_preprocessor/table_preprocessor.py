from abc import ABC, abstractmethod
import pandas as pd


class TablePreprocessor(ABC):
    """
    Modifies a rarity table. TablePreprocessors are applied sequentially.
    """
    @abstractmethod
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        pass
