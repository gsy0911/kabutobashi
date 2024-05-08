from dataclasses import dataclass

from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue, IBlockInput
from .abc_pre_process_block import IPreProcessBlock, IPreProcessBlockInput, IPreProcessBlockOutput


@dataclass(frozen=True)
class DefaultPreProcessBlockInput(IPreProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        input_params = block_glue.params.get("default_pre_process", {})
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

    def _process(self, block_input: IBlockInput) -> DefaultPreProcessBlockOutput:
        if not isinstance(block_input, DefaultPreProcessBlockInput):
            raise KabutobashiBlockInstanceMismatchError()

        required_cols = ["open", "high", "low", "close", "code", "volume"]
        df = block_input.series
        df = df[required_cols]
        return DefaultPreProcessBlockOutput.of(
            series=df,
            params=block_input.params,
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IPreProcessBlockInput, to=DefaultPreProcessBlockInput)
