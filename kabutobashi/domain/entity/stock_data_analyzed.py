from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cerberus import Validator
from mplfinance.original_flavor import candlestick_ohlc

from kabutobashi.errors import KabutobashiEntityError


@dataclass(frozen=True)
class StockDataAnalyzedBySingleMethod:
    """
    単一のmethodで処理した後のデータを保持
    可視化などを実行する際に利用
    """
    target_stock_code: Union[str, int]
    start_at: str
    end_at: str
    applied_method_name: str
    df_data: pd.DataFrame = field(repr=False)
    df_required_columns: List[str] = field(repr=False)
    parameters: Dict[str, Any]
    color_mapping: list = field(repr=False)
    visualize_option: dict = field(repr=False)

    @staticmethod
    def of(df: pd.DataFrame, method: "Method") -> "StockDataAnalyzedBySingleMethod":
        from kabutobashi.domain.method import Method

        # check all methods
        if not isinstance(method, Method):
            raise KabutobashiEntityError()

        return method.analyzed(df=df)

    def get_impact(self, influence: int = 2, tail: int = 5) -> Dict[str, float]:
        """

        Args:
            influence:
            tail:

        Returns:
            Dict[str, float]

        Examples:
        """
        return {self.applied_method_name: self._get_impact(df=self.df_data, influence=influence, tail=tail)}

    @staticmethod
    def _get_impact(df: pd.DataFrame, influence: int, tail: int) -> float:
        """
        売りと買いのシグナルの余波の合計値を返す。

        Args:
            _df:
            influence:
            tail:

        Returns:
            [-1,1]の値をとる。-1: 売り、1: 買いを表す
        """
        df["buy_impact"] = df["buy_signal"].ewm(span=influence).mean()
        df["sell_impact"] = df["sell_signal"].ewm(span=influence).mean()
        buy_impact_index = df["buy_impact"].iloc[-tail:].sum()
        sell_impact_index = df["sell_impact"].iloc[-tail:].sum()
        return round(buy_impact_index - sell_impact_index, 5)
