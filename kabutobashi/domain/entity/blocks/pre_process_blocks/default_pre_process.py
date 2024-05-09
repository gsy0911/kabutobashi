from dataclasses import dataclass

from injector import Binder, inject

from kabutobashi.domain.errors import (
    KabutobashiBlockInstanceMismatchError,
    KabutobashiBlockParamsIsNoneError,
    KabutobashiBlockSeriesIsNoneError,
)

from ..abc_block import BlockGlue
from .abc_pre_process_block import IPreProcessBlock, IPreProcessBlockInput, IPreProcessBlockOutput


@dataclass(frozen=True)
class DefaultPreProcessBlockInput(IPreProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        if block_glue.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        params = block_glue.params.get("default_pre_process", {})
        return cls(
            series=block_glue.series,
            params={"for_analysis": params.get("for_analysis", False)},
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

        params = self.block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")

        df = self.block_input.series
        for_analysis: bool = params["for_analysis"]
        if for_analysis:
            required_cols = ["open", "high", "low", "close", "code", "volume"]
            if df is None:
                raise KabutobashiBlockSeriesIsNoneError()
            df = df[required_cols]
        return DefaultPreProcessBlockOutput.of(
            series=df,
            params=self.block_input.params,
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IPreProcessBlockInput, to=DefaultPreProcessBlockInput)  # type: ignore[type-abstract]
