from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)  # type: ignore
class EstimateFilter(metaclass=ABCMeta):
    estimate_filter_name: str

    def estimate(self, data: dict) -> float:
        self._validate(data=data)
        return self._estimate(data=data)

    @abstractmethod
    def _validate(self, data: dict):
        raise NotImplementedError()

    @abstractmethod
    def _estimate(self, data: dict) -> float:
        raise NotImplementedError()


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


@dataclass(frozen=True)
class EfVolume(EstimateFilter):
    volume_threshold: int = 30_000
    estimate_filter_name: str = "volume"

    def _validate(self, data: dict):
        if "volume" not in data.keys():
            raise KeyError()

    def _estimate(self, data: dict) -> float:
        return 1 if data["volume"] >= self.volume_threshold else 0
