import os

import pandas as pd

PARENT_PATH = os.path.abspath(os.path.dirname(__file__))
SOURCE_PATH = os.path.abspath(os.path.dirname(PARENT_PATH))
DATA_PATH = f"{SOURCE_PATH}/data"


def example() -> pd.DataFrame:
    """

    Examples:
        >>> import kabutobashi as kb
        >>> records = kb.example()
        >>> agg = kb.StockCodeSingleAggregate.of(entity=records, code="1375")
        >>> processed = agg.with_processed(kb.methods)
    """
    file_name = "example.csv.gz"
    return pd.read_csv(f"{DATA_PATH}/{file_name}")
