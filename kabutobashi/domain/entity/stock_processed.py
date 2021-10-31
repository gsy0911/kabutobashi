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
    color_mapping: Optional[List[dict]]
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
    def of(_df: pd.DataFrame, methods: list) -> "StockProcessed":
        from kabutobashi.domain.method import Method

        # check all methods
        for method in methods:
            if not isinstance(method, Method):
                raise ValueError()

        initial_method: Method = methods[0]
        rest_methods: List[Method] = methods[1:]
        base = initial_method.process(_df=_df)

        for rest_method in rest_methods:
            base = base + rest_method.process(_df=_df)
        return base

    def _validate(self):
        pass

    def __add__(self, other: "StockProcessed") -> "StockProcessed":
        if not isinstance(other, StockProcessed):
            raise ValueError()

        # update
        color_mapping = []
        color_mapping.extend(self.color_mapping)
        color_mapping.extend(other.color_mapping)

        # update
        processed_dfs = {}
        processed_dfs.update(self.processed_dfs)
        processed_dfs.update(other.processed_dfs)
        return StockProcessed(
            code=self.code,
            methods=self.methods + other.methods,
            color_mapping=color_mapping,
            base_df=self.base_df,
            processed_dfs=processed_dfs
        )

    def get_impact(self, influence: int = 2, tail: int = 5) -> dict:
        return {k: self._get_impact(_df=v, influence=influence, tail=tail) for k, v in self.processed_dfs.items()}

    @staticmethod
    def _get_impact(_df: pd.DataFrame, influence: int, tail: int) -> float:
        """
        売りと買いのシグナルの余波の合計値を返す。

        Args:
            _df:
            influence:
            tail:

        Returns:
            [-1,1]の値をとる。-1: 売り、1: 買いを表す
        """
        _df["buy_impact"] = _df["buy_signal"].ewm(span=influence).mean()
        _df["sell_impact"] = _df["sell_signal"].ewm(span=influence).mean()
        buy_impact_index = _df["buy_impact"].iloc[-tail:].sum()
        sell_impact_index = _df["sell_impact"].iloc[-tail:].sum()
        return round(buy_impact_index - sell_impact_index, 5)
