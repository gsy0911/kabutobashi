from injector import Injector, inject, Binder
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Dict, Optional

import pandas as pd


@dataclass(frozen=True)
class IBlockInput(ABC):
    series: Optional[pd.DataFrame] = None
    params: Optional[dict] = None

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

    def process(self, block_input: IBlockInput) -> IBlockOutput:
        return self._process(block_input=block_input)

    @abstractmethod
    def _process(self, block_input: IBlockInput) -> IBlockOutput:
        raise NotImplementedError()


@dataclass(frozen=True)
class BlockGlue:
    series: Optional[pd.DataFrame] = None
    params: Optional[dict] = None
    block_outputs: Dict[str, IBlockOutput] = field(default_factory=dict, repr=False)

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


@inject
@dataclass(frozen=True)
class ILayer(ABC):
    block_input: IBlockInput
    block: IBlock

    @classmethod
    def of(cls):
        configured_injector = Injector(cls.configure)
        process_layer = configured_injector.get(cls)
        return process_layer

    @classmethod
    @abstractmethod
    def configure(cls, binder: Binder) -> None:
        raise NotImplementedError()

    def process(self, glue: BlockGlue) -> BlockGlue:
        block_output = self.block.process(block_input=self.block_input.of(glue))
        updated_glue = glue.update(block_output=block_output)
        return updated_glue
