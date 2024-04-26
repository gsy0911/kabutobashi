from dataclasses import dataclass

import pandas as pd

from ..abc_block import IBlockInput, IBlockOutput
from .abc_process_block import IProcessBlock


@dataclass(frozen=True)
class ProcessSmaBlockInput(IBlockInput):

    def _validate(self):
        pass


@dataclass(frozen=True)
class ProcessSmaBlockOutput(IBlockOutput):
    block_name: str = "process_sma"

    def _validate(self):
        pass


@dataclass(frozen=True)
class ProcessSmaBlock(IProcessBlock):
    short_term: int = 5
    medium_term: int = 21
    long_term: int = 70

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(
            sma_short=df["close"].rolling(self.short_term).mean(),
            sma_medium=df["close"].rolling(self.medium_term).mean(),
            sma_long=df["close"].rolling(self.long_term).mean(),
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df["diff"] = df.apply(lambda x: x["sma_long"] - x["sma_short"], axis=1)
        # 正負が交差した点
        df = df.join(self._cross(df["diff"]))
        df = df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df

    def _process(self, block_input: ProcessSmaBlockInput) -> ProcessSmaBlockOutput:
        applied_df = self._apply(df=block_input.series)
        signal_df = self._signal(df=applied_df)
        return ProcessSmaBlockOutput.of(
            series=signal_df[["sma_short", "sma_medium", "sma_long", "buy_signal", "sell_signal"]],
            params=block_input.params,
        )
