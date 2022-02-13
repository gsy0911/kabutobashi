from dataclasses import dataclass, field
from typing import Any, Dict, List, Union


@dataclass(frozen=True)
class StockDataEstimatedBySingleFilter:
    """ """

    target_stock_code: Union[str, int]
    estimated_value: float
    estimate_filter_name: str


@dataclass(frozen=True)
class StockDataEstimatedByMultipleFilter:
    """ """

    estimated: List[StockDataEstimatedBySingleFilter]
