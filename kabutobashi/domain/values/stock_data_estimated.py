from dataclasses import dataclass


@dataclass(frozen=True)
class StockDataEstimatedBySingleFilter:
    """
    StockDataEstimatedBySingleFilter: ValueObject
    """

    code: str
    estimated_value: float
    estimate_filter_name: str

    def weighted_estimated_value(self, weights: dict) -> float:
        weight = weights.get(self.estimate_filter_name, 1)
        return weight * self.estimated_value
