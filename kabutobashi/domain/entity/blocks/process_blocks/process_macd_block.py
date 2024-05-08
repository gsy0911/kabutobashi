from dataclasses import dataclass

import pandas as pd
from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue
from .abc_process_block import IProcessBlock, IProcessBlockInput, IProcessBlockOutput

__all__ = ["ProcessMacdBlock"]


@dataclass(frozen=True)
class ProcessMacdBlockInput(IProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        if block_glue.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        input_params = block_glue.params.get("process_macd", {})
        short_term = input_params.get("short_term", 12)
        long_term = input_params.get("long_term", 26)
        macd_span = input_params.get("macd_span", 9)
        return cls(
            series=block_glue.series,
            params={
                "short_term": short_term,
                "long_term": long_term,
                "macd_span": macd_span,
            },
        )

    def _validate(self):
        pass


@dataclass(frozen=True)
class ProcessMacdBlockOutput(IProcessBlockOutput):
    block_name: str = "process_macd"

    def _validate(self):
        pass


@inject
@dataclass(frozen=True)
class ProcessMacdBlock(IProcessBlock):

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:
        input_params = self.block_input.params
        if input_params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        short_term = input_params["short_term"]
        long_term = input_params["long_term"]
        macd_span = input_params["macd_span"]

        df = df.assign(
            # MACDの計算
            ema_short=lambda x: x["close"].ewm(span=short_term).mean(),
            ema_long=lambda x: x["close"].ewm(span=long_term).mean(),
            macd=lambda x: x["ema_short"] - x["ema_long"],
            signal=lambda x: x["macd"].ewm(span=macd_span).mean(),
            # ヒストグラム値
            histogram=lambda x: x["macd"] - x["signal"],
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        # 正負が交差した点
        df = df.join(self._cross(df["histogram"]))
        df = df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df

    def _process(self) -> ProcessMacdBlockOutput:
        if not isinstance(self.block_input, ProcessMacdBlockInput):
            raise KabutobashiBlockInstanceMismatchError()
        applied_df = self._apply(df=self.block_input.series)
        signal_df = self._signal(df=applied_df)
        return ProcessMacdBlockOutput.of(
            series=signal_df[["ema_short", "ema_long", "macd", "signal", "histogram", "buy_signal", "sell_signal"]],
            params=self.block_input.params,
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IProcessBlockInput, to=ProcessMacdBlockInput)  # type: ignore[type-abstract]
