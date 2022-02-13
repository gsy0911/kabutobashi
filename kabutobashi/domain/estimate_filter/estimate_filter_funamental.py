from .estimate_filter import EstimateFilter
from dataclasses import dataclass


@dataclass(frozen=True)
class EfFundamental(EstimateFilter):
    estimate_filter_name: str = "fundamental"

    def _validate(self, data: dict):
        pass

    def _estimate(self, data: dict) -> float:
        return 0.5
