from dataclasses import dataclass, field
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import pandas as pd

from kabutobashi.domain.errors import KabutobashiEntityError


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

    def __post_init__(self):
        df_columns = self.df.columns
        if not all([c in df_columns for c in self.df_required_columns]):
            raise KabutobashiEntityError()

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


@dataclass(frozen=True)
class StockDataVisualized:
    """
    StockDataVisualized: ValueObject
    Used to visualize.
    """

    fig: plt.Figure
    size_ratio: int

    def __post_init__(self):
        if type(self.fig) is not plt.Figure:
            raise KabutobashiEntityError()


@dataclass(frozen=True)
class StockDataEstimated:
    """
    StockDataEstimatedBySingleFilter: ValueObject
    """

    code: str
    estimated_value: float
    estimate_filter_name: str

    def weighted_estimated_value(self, weights: dict) -> float:
        weight = weights.get(self.estimate_filter_name, 1)
        return weight * self.estimated_value
