from dataclasses import dataclass, field
from typing import Any, Dict, List, Union


@dataclass(frozen=True)
class StockDataEstimatedBySingleFilter:
    """ """

    target_stock_code: Union[str, int]
    estimated_value: float
    estimate_filter_name: str

    def weighted_estimated_value(self, weights: dict) -> float:
        weight = weights.get(self.estimate_filter_name, 1)
        return weight * self.estimated_value


@dataclass(frozen=True)
class StockDataEstimatedByMultipleFilter:
    """ """

    estimated: List[StockDataEstimatedBySingleFilter]

    def weighted_estimated_value(self, weights: dict = None) -> float:
        if not weights:
            weights = {}
        return sum([e.weighted_estimated_value(weights=weights) for e in self.estimated])
