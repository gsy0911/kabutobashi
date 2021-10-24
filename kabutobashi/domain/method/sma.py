from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd

from .method import Method


@dataclass(frozen=True)
class SMA(Method):
    short_term: int = 5
    medium_term: int = 21
    long_term: int = 70
    method_name: str = "sma"

    def _method(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.assign(
            sma_short=_df["close"].rolling(self.short_term).mean(),
            sma_medium=_df["close"].rolling(self.medium_term).mean(),
            sma_long=_df["close"].rolling(self.long_term).mean(),
        )
        return _df

    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df["diff"] = _df.apply(lambda x: x["sma_long"] - x["sma_short"], axis=1)
        # 正負が交差した点
        _df = _df.join(self._cross(_df["diff"]))
        _df = _df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return _df

    def _visualize(self, _df: pd.DataFrame):
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(6, 5))
        # x軸のオートフォーマット
        fig.autofmt_xdate()

        # set candlestick
        self.add_ax_candlestick(ax, _df)

        # plot macd
        ax.plot(_df.index, _df["sma_long"], color="#dc143c", label="sma_long")
        ax.plot(_df.index, _df["sma_medium"], color="#ffa500", label="sma_medium")
        ax.plot(_df.index, _df["sma_short"], color="#1e90ff", label="sma_short")

        ax.legend(loc="best")  # 各線のラベルを表示
        return fig
