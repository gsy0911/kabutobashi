from dataclasses import dataclass
from typing import List, Union


@dataclass(frozen=True)
class StockDataEstimatedBySingleFilter:
    """ """

    code: str
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

    def estimate_filter_concat_name(self) -> str:
        estimate_filter_names = sorted([e.estimate_filter_name for e in self.estimated])
        return "_".join(estimate_filter_names)
