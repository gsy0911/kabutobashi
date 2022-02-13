from dataclasses import dataclass

from .estimate_filter import EstimateFilter


@dataclass(frozen=True)
class EfFundamental(EstimateFilter):
    estimate_filter_name: str = "fundamental"

    def _validate(self, data: dict):
        if "sma" not in data.keys():
            raise KeyError()
        if "macd" not in data.keys():
            raise KeyError()
        if "stochastics" not in data.keys():
            raise KeyError()
        if "bollinger_bands" not in data.keys():
            raise KeyError()
        if "momentum" not in data.keys():
            raise KeyError()
        if "psycho_logical" not in data.keys():
            raise KeyError()

    def _estimate(self, data: dict) -> float:
        return (
            data["sma"] * 1.5
            + data["macd"] * 1.1
            + data["stochastics"] * 0.2
            + data["bollinger_bands"]
            + data["momentum"]
            + data["psycho_logical"]
        )
