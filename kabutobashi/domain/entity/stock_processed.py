from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Union

from cerberus import Validator
import pandas as pd
#
from kabutobashi.errors import KabutobashiEntityError


@dataclass(frozen=True)
class StockProcessed:
    """
    methodで処理した後のデータを保持
    可視化などを実行する際に利用

    """
    code: Optional[Union[str, int]]
    # str: methods, pd.DataFrame: ProcessedDataFrame
    methods: List[str]
    color_mapping: Optional[dict]
    base_df: pd.DataFrame = field(repr=False)
    processed_dfs: Dict[str, pd.DataFrame] = field(repr=False)

    BASE_DF_SCHEMA = {
        "code": {"type": "string"},
        "open": {"type": "float"},
        "high": {"type": "float"},
        "low": {"type": "float"},
        "close": {"type": "float"},
        "dt": {"type": "string"},
    }

    @staticmethod
    def of(_df: pd.DataFrame, methods: list):
        from kabutobashi.domain.method import Method
        pass

    def _validate(self):
        pass

    def __add__(self, other: "StockProcessed") -> "StockProcessed":
        pass
