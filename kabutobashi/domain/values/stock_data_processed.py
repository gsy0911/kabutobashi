from dataclasses import dataclass, field
from typing import Any, Dict, List

import pandas as pd


@dataclass(frozen=True)
class StockDataProcessed:
    """
    StockDataProcessedBySingleMethod: ValueObject
    Holds data processed by singular-Method.
    """

    code: str
    start_at: str
    end_at: str
    applied_method_name: str
    df: pd.DataFrame = field(repr=False)
    df_required_columns: List[str] = field(repr=False)
    parameters: Dict[str, Any]

    def get_impact(self, influence: int = 2, tail: int = 5) -> Dict[str, float]:
        """

        Args:
            influence:
            tail:

        Returns:
            Dict[str, float]

        Examples:
        """
        return {self.applied_method_name: self._get_impact(df=self.df, influence=influence, tail=tail)}

    @staticmethod
    def _get_impact(df: pd.DataFrame, influence: int, tail: int) -> float:
        """
        売りと買いのシグナルの余波の合計値を返す。

        Args:
            df:
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
