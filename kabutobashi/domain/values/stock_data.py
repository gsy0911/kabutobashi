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
    impact: float

    def __post_init__(self):
        df_columns = self.df.columns
        if not all([c in df_columns for c in self.df_required_columns]):
            raise KabutobashiEntityError()

    def get_impact(self) -> Dict[str, float]:
        return {self.applied_method_name: self.impact}


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
