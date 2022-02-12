from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cerberus import Validator
from mplfinance.original_flavor import candlestick_ohlc

from kabutobashi.errors import KabutobashiEntityError


@dataclass(frozen=True)
class StockDataAnalyzedBySingleMethod:
    """
    単一のmethodで処理した後のデータを保持
    可視化などを実行する際に利用
    """
    target_stock_code: Union[str, int]
    start_at: str
    end_at: str
    applied_method_name: str
    df_data: pd.DataFrame = field(repr=False)
    df_required_columns: List[str] = field(repr=False)
    parameters: Dict[str, Any]
    color_mapping: list = field(repr=False)
    visualize_option: dict = field(repr=False)

    @staticmethod
    def of(df: pd.DataFrame, method: "Method") -> "StockDataAnalyzedBySingleMethod":
        from kabutobashi.domain.method import Method

        # check all methods
        if not isinstance(method, Method):
            raise KabutobashiEntityError()

        return method.analyzed(df=df)

    def get_impact(self, influence: int = 2, tail: int = 5) -> Dict[str, float]:
        """

        Args:
            influence:
            tail:

        Returns:
            Dict[str, float]

        Examples:
        """
        return {self.applied_method_name: self._get_impact(df=self.df_data, influence=influence, tail=tail)}

    @staticmethod
    def _get_impact(df: pd.DataFrame, influence: int, tail: int) -> float:
        """
        売りと買いのシグナルの余波の合計値を返す。

        Args:
            df:
            influence:
            tail:

        Returns:
            [-1,1]の値をとる。-1: 売り、1: 買いを表す
        """
        df["buy_impact"] = df["buy_signal"].ewm(span=influence).mean()
        df["sell_impact"] = df["sell_signal"].ewm(span=influence).mean()
        buy_impact_index = df["buy_impact"].iloc[-tail:].sum()
        sell_impact_index = df["sell_impact"].iloc[-tail:].sum()
        return round(buy_impact_index - sell_impact_index, 5)


@dataclass(frozen=True)
class StockDataAnalyzedByMultipleMethod:
    analyzed: List[StockDataAnalyzedBySingleMethod] = field(default_factory=list)

    @staticmethod
    def of(df: pd.DataFrame, methods: List["Method"]) -> "StockDataAnalyzedByMultipleMethod":
        from kabutobashi.domain.method import Method

        # check all methods
        for method in methods:
            if not isinstance(method, Method):
                raise KabutobashiEntityError()

        return StockDataAnalyzedByMultipleMethod(analyzed=[m.analyzed(df=df) for m in methods])

    @staticmethod
    def _add_ax_candlestick(ax, _df: pd.DataFrame):
        # datetime -> float
        time_series = mdates.date2num(_df["dt"])
        data = _df[["open", "high", "low", "close"]].values.T
        # data
        ohlc = np.vstack((time_series, data)).T
        candlestick_ohlc(ax, ohlc, width=0.7, colorup="g", colordown="r")

    def visualize(self, size_ratio: int = 2):
        """
        macdはlower
        sma、bolinger_bandsは同じところに表示させる。
        買いのポイントも表示させる

        Returns:

        """

        def _n_rows() -> int:
            lower_nums = len([p for p in self.analyzed if p.visualize_option["position"] == "lower"])
            return 1 + lower_nums

        n_rows = _n_rows()

        def _gridspec_kw() -> dict:
            if n_rows == 1:
                return {"height_ratios": [3]}
            return {"height_ratios": [3] + [1] * (n_rows - 1)}

        gridspec_kw = _gridspec_kw()
        fig, axs = plt.subplots(
            nrows=n_rows, ncols=1, figsize=(6 * size_ratio, 5 * size_ratio), gridspec_kw=gridspec_kw
        )
        # auto-formatting x-axis
        fig.autofmt_xdate()

        # set candlestick base
        base_df = self.analyzed[0].df_data[["dt", "open", "close", "high", "low"]]
        self._add_ax_candlestick(axs[0], base_df)

        ax_idx = 1
        # plots
        for processed in self.analyzed:
            position = processed.visualize_option["position"]
            df = processed.df_data
            time_series = mdates.date2num(df["dt"])
            mapping = processed.color_mapping
            if position == "in":
                for m in mapping:
                    df_key = m["df_key"]
                    color = m["color"]
                    label = m["label"]
                    axs[0].plot(time_series, df[df_key], label=label)
                # display labels
                axs[0].legend(loc="best")
            elif position == "lower":
                for m in mapping:
                    df_key = m["df_key"]
                    color = m["color"]
                    label = m["label"]
                    plot = m.get("plot", "plot")
                    if plot == "plot":
                        # type FloatingArray is no accepted ...
                        # so `df[df_key].astype(float)`
                        axs[ax_idx].plot(time_series, df[df_key].astype(float), label=label)
                    elif plot == "bar":
                        axs[ax_idx].bar(time_series, df[df_key], label=label)
                # display labels
                axs[ax_idx].legend(loc="best")
                # lower
                ax_idx += 1
            elif position == "-":
                # technical_analysis以外のmethodが入っている場合
                pass
            else:
                raise KabutobashiEntityError()

        return fig

