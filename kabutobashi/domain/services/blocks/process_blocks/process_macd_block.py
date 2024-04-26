from dataclasses import dataclass

import pandas as pd

from ..abc_block import IBlockInput, IBlockOutput
from .abc_process_block import IProcessBlock


@dataclass(frozen=True)
class ProcessMacdBlockInput(IBlockInput):

    def _validate(self):
        pass


@dataclass(frozen=True)
class ProcessMacdBlockOutput(IBlockOutput):
    block_name: str = "process_macd"

    def _validate(self):
        pass


@dataclass(frozen=True)
class ProcessMacdBlock(IProcessBlock):
    short_term: int = 12
    long_term: int = 26
    macd_span: int = 9

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(
            # MACDの計算
            ema_short=lambda x: x["close"].ewm(span=self.short_term).mean(),
            ema_long=lambda x: x["close"].ewm(span=self.long_term).mean(),
            macd=lambda x: x["ema_short"] - x["ema_long"],
            signal=lambda x: x["macd"].ewm(span=self.macd_span).mean(),
            # ヒストグラム値
            histogram=lambda x: x["macd"] - x["signal"],
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        # 正負が交差した点
        df = df.join(self._cross(df["histogram"]))
        df = df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df

    def _process(self, block_input: ProcessMacdBlockInput) -> ProcessMacdBlockOutput:
        applied_df = self._apply(df=block_input.series)
        signal_df = self._signal(df=applied_df)
        return ProcessMacdBlockOutput.of(
            series=signal_df[["ema_short", "ema_long", "macd", "signal", "histogram", "buy_signal", "sell_signal"]],
            params=block_input.params,
        )
