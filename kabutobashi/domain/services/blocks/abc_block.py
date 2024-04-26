from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import pandas as pd


@dataclass(frozen=True)
class IBlockInput(ABC):
    series: pd.DataFrame
    params: dict

    def __post_init__(self):
        self.validate()

    def validate(self):
        self._validate()

    @abstractmethod
    def _validate(self):
        raise NotImplementedError()


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
class IBlock(ABC):

    def process(self, block_input) -> IBlockOutput:
        block_input.validate()
        return self._process(block_input=block_input)

    @abstractmethod
    def _process(self, block_input: IBlockInput) -> IBlockOutput:
        raise NotImplementedError()
