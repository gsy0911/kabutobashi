from dataclasses import dataclass

import matplotlib.pyplot as plt
import pandas as pd

from .method import Method


@dataclass(frozen=True)
class PsychoLogical(Method):
    """
    See Also:
        https://www.sevendata.co.jp/shihyou/technical/psycho.html
    """

    upper_threshold: float = 0.75
    lower_threshold: float = 0.25
    psycho_term: float = 12
    method_name: str = "psycho_logical"

    def _method(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df["shift_close"] = _df["close"].shift(1)
        _df["diff"] = _df.apply(lambda x: x["close"] - x["shift_close"], axis=1)

        _df["is_raise"] = _df["diff"].apply(lambda x: 1 if x > 0 else 0)

        _df["psycho_sum"] = _df["is_raise"].rolling(self.psycho_term).sum()
        _df["psycho_line"] = _df["psycho_sum"].apply(lambda x: x / self.psycho_term)

        _df["bought_too_much"] = _df["psycho_line"].apply(lambda x: 1 if x > self.upper_threshold else 0)
        _df["sold_too_much"] = _df["psycho_line"].apply(lambda x: 1 if x < self.lower_threshold else 0)
        return _df

    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df["buy_signal"] = _df["sold_too_much"]
        _df["sell_signal"] = _df["bought_too_much"]
        return _df

    def _visualize(self, _df: pd.DataFrame):
        fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, gridspec_kw={"height_ratios": [3, 1]}, figsize=(6, 5))
        # x軸のオートフォーマット
        fig.autofmt_xdate()

        # set candlestick
        self.add_ax_candlestick(ax1, _df)

        # plot
        ax2.plot(_df.index, _df["psycho_line"], label="psycho_line")
        ax2.legend(loc="center left")  # 各線のラベルを表示

        ax1.legend(loc="best")  # 各線のラベルを表示
        return fig
