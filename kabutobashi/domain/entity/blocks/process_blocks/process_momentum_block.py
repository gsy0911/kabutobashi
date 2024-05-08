from dataclasses import dataclass

import pandas as pd
from injector import Binder, inject
from overrides import override

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue, IBlockInput
from .abc_process_block import IProcessBlock, IProcessBlockInput, IProcessBlockOutput


@dataclass(frozen=True)
class ProcessMomentumBlockInput(IProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        input_params = block_glue.params.get("process_momentum", {})
        term = input_params.get("term", 12)
        return cls(
            series=block_glue.series,
            params={
                "term": term,
            },
        )

    def _validate(self):
        pass


@dataclass(frozen=True)
class ProcessMomentumBlockOutput(IProcessBlockOutput):
    block_name: str = "process_momentum"

    def _validate(self):
        pass


@inject
@dataclass(frozen=True)
class ProcessMomentumBlock(IProcessBlock):

    @override
    def _apply(self, df: pd.DataFrame, term: int) -> pd.DataFrame:
        df = df.assign(
            momentum=df["close"].shift(10),
        ).fillna(0)
        df = df.assign(sma_momentum=lambda x: x["momentum"].rolling(term).mean())
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.join(self._cross(df["sma_momentum"]))
        df = df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df

    def _process(self, block_input: IBlockInput) -> ProcessMomentumBlockOutput:
        if not isinstance(block_input, ProcessMomentumBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        term = block_input.params["term"]
        params = block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")

        applied_df = self._apply(df=block_input.series, term=term)
        signal_df = self._signal(df=applied_df)
        required_columns = ["momentum", "sma_momentum", "buy_signal", "sell_signal"]
        return ProcessMomentumBlockOutput.of(
            series=signal_df[required_columns],
            params=block_input.params,
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IProcessBlockInput, to=ProcessMomentumBlockInput)
