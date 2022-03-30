from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cerberus import Validator
from mplfinance.original_flavor import candlestick_ohlc

from kabutobashi import EstimateFilter
from kabutobashi.errors import KabutobashiEntityError

from .stock_data_estimated import StockDataEstimatedByMultipleFilter, StockDataEstimatedBySingleFilter


@dataclass(frozen=True)
class StockDataProcessedBySingleMethod:
    """
    Holds data processed by singular-Method.
    """

    code: str
    start_at: str
    end_at: str
    applied_method_name: str
    df: pd.DataFrame = field(repr=False)
    df_required_columns: List[str] = field(repr=False)
    parameters: Dict[str, Any]
    color_mapping: list = field(repr=False)
    visualize_option: dict = field(repr=False)
    COLOR_MAPPING_SCHEMA = {
        "df_key": {"type": "string"},
        "color": {"type": "string"},
        "label": {"type": "string"},
        "plot": {"type": "string", "allowed": ["plot", "bar"], "required": False},
    }
    VISUALIZE_OPTION_SCHEMA = {"position": {"type": "string", "allowed": ["in", "lower", "-"]}}

    def __post_init__(self):
        self._check_color_mapping(data=self.color_mapping)
        self._check_visualize_option(data=self.visualize_option)

    def _check_color_mapping(self, data: list):
        validator = Validator(self.COLOR_MAPPING_SCHEMA)
        for d in data:
            if not validator.validate(d):
                raise KabutobashiEntityError(validator)

    def _check_visualize_option(self, data: dict):
        validator = Validator(self.VISUALIZE_OPTION_SCHEMA)
        if not validator.validate(data):
            raise KabutobashiEntityError(validator)

    def get_impact(self, influence: int = 2, tail: int = 5) -> Dict[str, float]:
        """

        Args:
            influence:
            tail:

        Returns:
            Dict[str, float]

        Examples:
        """
        return {self.applied_method_name: self._get_impact(df=self.df, influence=influence, tail=tail)}

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
class StockDataProcessedByMultipleMethod:
    """
    Holds data processed by multiple-Methods.
    Also used to visualize.
    """

    processed: List[StockDataProcessedBySingleMethod] = field(default_factory=list)

    @staticmethod
    def _add_ax_candlestick(ax, _df: pd.DataFrame):
        # datetime -> float
        time_series = mdates.date2num(_df["dt"])
        data = _df[["open", "high", "low", "close"]].values.T
        # data
        ohlc = np.vstack((time_series, data)).T
        candlestick_ohlc(ax, ohlc, width=0.7, colorup="g", colordown="r")

    def get_impact(self, influence: int = 2, tail: int = 5) -> Dict[str, float]:
        data = {}
        for a in self.processed:
            data.update(a.get_impact(influence=influence, tail=tail))
        return data

    def get_parameters(self):
        data = {}
        for a in self.processed:
            data.update(a.parameters)
        return data

    def visualize(self, size_ratio: int = 2):
        """
        Visualize Stock Data.

        Args:
            size_ratio: determine the size of the graph, default 2.

        Returns:
            Figure
        """

        def _n_rows() -> int:
            lower_nums = len([p for p in self.processed if p.visualize_option["position"] == "lower"])
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
        base_df = self.processed[0].df[["dt", "open", "close", "high", "low"]]
        self._add_ax_candlestick(axs[0], base_df)

        ax_idx = 1
        # plots
        for processed in self.processed:
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

    def _to_single_estimated(
        self, estimate_filter: EstimateFilter, data: Optional[dict] = None
    ) -> StockDataEstimatedBySingleFilter:
        if not data:
            data = {}
            data.update(self.get_impact())
            data.update(self.get_parameters())
        return StockDataEstimatedBySingleFilter(
            code=self.processed[0].code,
            estimate_filter_name=estimate_filter.estimate_filter_name,
            estimated_value=estimate_filter.estimate(data=data),
        )

    def to_estimated(self, estimate_filters: List[EstimateFilter]) -> StockDataEstimatedByMultipleFilter:
        """

        Returns:
            StockDataEstimatedByMultipleFilter
        """
        data = {}
        data.update(self.get_impact())
        data.update(self.get_parameters())
        return StockDataEstimatedByMultipleFilter(
            estimated=[self._to_single_estimated(estimate_filter=ef) for ef in estimate_filters]
        )
