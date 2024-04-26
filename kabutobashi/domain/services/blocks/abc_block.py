from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Optional

import pandas as pd


@dataclass(frozen=True)
class IBlockInput(ABC):
    series: pd.DataFrame
    params: dict

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        return cls(series=block_glue.series, params=block_glue.params)

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
    block_input: IBlockInput

    def process(self) -> IBlockOutput:
        return self._process(block_input=self.block_input)

    @abstractmethod
    def _process(self, block_input: IBlockInput) -> IBlockOutput:
        raise NotImplementedError()


@dataclass(frozen=True)
class BlockGlue:
    series: pd.DataFrame
    params: dict
    block_outputs: Dict[str, IBlockOutput] = field(default_factory=dict)

    def update(self, block_output: IBlockOutput) -> "BlockGlue":
        self.block_outputs[block_output.block_name] = block_output
        return self
