from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Dict, Optional

import pandas as pd
from injector import Binder, Injector, inject


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


@inject
@dataclass(frozen=True)
class IBlock(ABC):
    block_input: Optional[IBlockInput]

    def process(self) -> IBlockOutput:
        return self._process()

    @abstractmethod
    def _process(self) -> IBlockOutput:
        raise NotImplementedError()

    @classmethod
    def glue(cls, glue: "BlockGlue") -> "BlockGlue":
        block = Injector(cls._configure).get(cls)
        if block.block_input is None:
            raise ValueError("Block inputs cannot be None")
        updated_block = replace(cls(block_input=None), block_input=block.block_input.of(block_glue=glue))
        updated_glue = glue.update(block_output=updated_block.process())
        return updated_glue

    @classmethod
    @abstractmethod
    def _configure(cls, binder: Binder) -> None:
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
