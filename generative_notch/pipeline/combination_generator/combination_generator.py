import pandas as pd
from abc import ABC, abstractmethod
from attrs import define


@define
class CombinationGenerator(ABC):
    """
    Generates combinations from given rarity table. Can implement any algorithm for deducing the output combinations.
    """
    n: int
    save_filepath: str

    @abstractmethod
    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    # TODO DO I need to use save using interface method?
    @abstractmethod
    def save(self):
        pass
