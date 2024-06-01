import pandas as pd

from ..decorator import block
from .abc_process_block import cross

__all__ = ["ProcessMacdBlock"]


@block(block_name="process_macd", series_required_columns=["close"])
class ProcessMacdBlock:
    series: pd.DataFrame
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
        df = df.join(cross(df["histogram"]))
        df = df.rename(columns={"to_plus": "macd_buy_signal", "to_minus": "macd_sell_signal"})
        return df

    def _process(self) -> pd.DataFrame:
        applied_df = self._apply(df=self.series)
        signal_df = self._signal(df=applied_df)
        return signal_df[
            ["ema_short", "ema_long", "macd", "signal", "histogram", "macd_buy_signal", "macd_sell_signal"]
        ]
