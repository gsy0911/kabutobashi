from dataclasses import dataclass

from injector import Binder, inject

from kabutobashi.domain.errors import (
    KabutobashiBlockInstanceMismatchError,
    KabutobashiBlockParamsIsNoneError,
    KabutobashiBlockSeriesIsNoneError,
)

from ..abc_block import BlockGlue, IBlockInput
from .abc_pre_process_block import IPreProcessBlock, IPreProcessBlockInput, IPreProcessBlockOutput


@dataclass(frozen=True)
class DefaultPreProcessBlockInput(IPreProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        return cls(
            series=block_glue.series,
            params={},
        )

    def _validate(self):
        pass


@dataclass(frozen=True)
class DefaultPreProcessBlockOutput(IPreProcessBlockOutput):
    block_name: str = "default_pre_process"

    def _validate(self):
        pass


@inject
@dataclass(frozen=True)
class DefaultPreProcessBlock(IPreProcessBlock):

    def _process(self) -> DefaultPreProcessBlockOutput:
        if not isinstance(self.block_input, DefaultPreProcessBlockInput):
            raise KabutobashiBlockInstanceMismatchError()

        required_cols = ["open", "high", "low", "close", "code", "volume"]
        df = self.block_input.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        df = df[required_cols]
        return DefaultPreProcessBlockOutput.of(
            series=df,
            params=self.block_input.params,
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IBlockInput, to=DefaultPreProcessBlockInput)  # type: ignore[type-abstract]
