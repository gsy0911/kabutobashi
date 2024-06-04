from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Dict, Optional

import pandas as pd


@dataclass(frozen=True)
class IBlockOutput(ABC):
    series: Optional[pd.DataFrame]
    params: Optional[dict]
    block_name: str = "block"

    def __post_init__(self):
        self.validate()

    @classmethod
    def of(cls, series: Optional[pd.DataFrame], params: Optional[dict]):
        return cls(series, params)

    def validate(self):
        self._validate()

    @abstractmethod
    def _validate(self):
        raise NotImplementedError()


@dataclass(frozen=True)
class IBlock:
    pass


@dataclass(frozen=True)
class BlockGlue:
    series: Optional[pd.DataFrame] = None
    params: Optional[dict] = None
    block_outputs: Dict[str, IBlockOutput] = field(default_factory=dict, repr=False)
    execution_order: int = 1

    def update(self, block_output: IBlockOutput) -> "BlockGlue":
        self.block_outputs[block_output.block_name] = block_output
        if self.series is None:
            series = block_output.series
        else:
            series = self.series

        if self.params is None:
            params = block_output.params
        else:
            params = self.params
        return replace(self, series=series, params=params, block_outputs=self.block_outputs)

    def __len__(self):
        return len(self.block_outputs.keys())

    def __getitem__(self, key: str):
        if type(key) is str:
            return self.block_outputs[key]
        else:
            raise KeyError(f"Key {key} is not a str")

    def __iter__(self):
        for k, v in self.block_outputs.items():
            yield k, v

    def __contains__(self, item: str):
        if type(item) is str:
            return item in self.block_outputs.keys()
        else:
            raise KeyError(f"Key {item} is not a str")
