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
