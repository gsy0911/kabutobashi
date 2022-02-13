from dataclasses import dataclass

from .estimate_filter import EstimateFilter


@dataclass(frozen=True)
class EfVolume(EstimateFilter):
    volume_threshold: int = 30_000
    estimate_filter_name: str = "volume"

    def _validate(self, data: dict):
        if "volume" not in data.keys():
            raise KeyError()

    def _estimate(self, data: dict) -> float:
        return 1 if data["volume"] >= self.volume_threshold else 0
