from attrs import define
import pandas as pd
from generative_notch import get_config
from .table_preprocessor import TablePreprocessor


@define
class NormalizeWeightsTablePreprocessor(TablePreprocessor):
    """
    Re-scale target weights to range 0:1 in secluded feature groups
    """

    table_config: dict

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        return normalize_weights_in_groups(
            df=df,
            group_column_name=self.table_config['feature_column_name'],
            weights_column_name=self.table_config['weights_column_name']
        )


def normalize_weights_in_groups(df: pd.DataFrame, group_column_name: str, weights_column_name: str) -> pd.DataFrame:
    return (
        df
        .assign(**{weights_column_name: lambda d: d
                .groupby(group_column_name)
                [weights_column_name]
                .apply(lambda x: x / x.sum())}
        )
    )
