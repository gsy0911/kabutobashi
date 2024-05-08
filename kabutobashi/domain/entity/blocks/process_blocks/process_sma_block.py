from dataclasses import dataclass

import pandas as pd
from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue
from .abc_process_block import IProcessBlock, IProcessBlockInput, IProcessBlockOutput

__all__ = ["ProcessSmaBlock"]


@dataclass(frozen=True)
class ProcessSmaBlockInput(IProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        params = block_glue.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        input_params = params.get("process_macd", {})
        short_term = input_params.get("short_term", 5)
        medium_term = input_params.get("medium_term", 21)
        long_term = input_params.get("long_term", 70)
        return cls(
            series=block_glue.series,
            params={
                "short_term": short_term,
                "medium_term": medium_term,
                "long_term": long_term,
            },
        )

    def _validate(self):
        pass


@dataclass(frozen=True)
class ProcessSmaBlockOutput(IProcessBlockOutput):
    block_name: str = "process_sma"

    def _validate(self):
        pass


@inject
@dataclass(frozen=True)
class ProcessSmaBlock(IProcessBlock):

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:
        input_params = self.block_input.params
        if input_params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        short_term = input_params["short_term"]
        medium_term = input_params["medium_term"]
        long_term = input_params["long_term"]

        df = df.assign(
            sma_short=df["close"].rolling(short_term).mean(),
            sma_medium=df["close"].rolling(medium_term).mean(),
            sma_long=df["close"].rolling(long_term).mean(),
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df["diff"] = df.apply(lambda x: x["sma_long"] - x["sma_short"], axis=1)
        # 正負が交差した点
        df = df.join(self._cross(df["diff"]))
        df = df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df

    def _process(self) -> ProcessSmaBlockOutput:
        if not isinstance(self.block_input, ProcessSmaBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        applied_df = self._apply(df=self.block_input.series)
        signal_df = self._signal(df=applied_df)
        return ProcessSmaBlockOutput.of(
            series=signal_df[["sma_short", "sma_medium", "sma_long", "buy_signal", "sell_signal"]],
            params=self.block_input.params,
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IProcessBlockInput, to=ProcessSmaBlockInput)
