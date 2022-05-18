from dataclasses import dataclass, field
from typing import List

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc

from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.domain.values.stock_data_processed import StockDataProcessedBySingleMethod


@dataclass(frozen=True)
class StockDataVisualized:
    """
    StockDataVisualized: ValueObject
    Used to visualize.
    """

    fig: plt.Figure
    size_ratio: int
    processed: List[StockDataProcessedBySingleMethod] = field(default_factory=list)

    @staticmethod
    def of(processed: List[StockDataProcessedBySingleMethod], size_ratio: int = 2):
        return StockDataVisualized(
            fig=StockDataVisualized._visualize(processed_list=processed, size_ratio=size_ratio), size_ratio=size_ratio
        )

    @staticmethod
    def _add_ax_candlestick(ax, _df: pd.DataFrame):
        # datetime -> float
        time_series = mdates.date2num(_df["dt"])
        data = _df[["open", "high", "low", "close"]].values.T
        # data
        ohlc = np.vstack((time_series, data)).T
        candlestick_ohlc(ax, ohlc, width=0.7, colorup="g", colordown="r")

    @staticmethod
    def _visualize(processed_list: List[StockDataProcessedBySingleMethod], size_ratio: int):
        """
        Visualize Stock Data.

        Args:
            processed_list:
            size_ratio: determine the size of the graph, default 2.

        Returns:
            Figure
        """

        def _n_rows() -> int:
            lower_nums = len([p for p in processed_list if p.visualize_option["position"] == "lower"])
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
        base_df = processed_list[0].df[["dt", "open", "close", "high", "low"]]
        StockDataVisualized._add_ax_candlestick(axs[0], base_df)

        ax_idx = 1
        # plots
        for processed in processed_list:
            position = processed.visualize_option["position"]
            df = processed.df
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
