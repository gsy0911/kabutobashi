from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Optional

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
from pydantic import BaseModel, ConfigDict

from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.domain.values import StockDataProcessed, StockDataVisualized

__all__ = ["ProcessMethod", "VisualizeMethod", "Method", "MethodType"]


class MethodType(Enum):
    TECHNICAL_ANALYSIS = auto()
    PARAMETERIZE = auto()
    CROSS_SECTION = auto()
    SIGNAL_PROCESSING = auto()


class ProcessMethod(ABC, BaseModel):
    """
    株のテクニカル分析に関するメソッドを提供するクラス

    Examples:
        >>> import pandas as pd
        >>> import kabutobashi as kb
        >>> stock_df: pd.DataFrame = pd.DataFrame("path_to_stock_data")
        # get sma-based-analysis
        >>> sma_df = stock_df.pipe(kb.sma)
        # get sma-base-buy or sell signal
        >>> sma_signal = stock_df.pipe(kb.sma, impact="true", influence=5, tail=5)
        # get macd-based-analysis
        >>> macd_df = stock_df.pipe(kb.macd)
        # get macd-base-buy or sell signal
        >>> sma_signal = stock_df.pipe(kb.macd, impact="true", influence=5, tail=5)
    """

    # 名前
    method_name: str
    # 種類:
    method_type: MethodType
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def process(self, df: pd.DataFrame, influence: int = 2, tail: int = 5) -> "StockDataProcessed":
        code_list = list(set(df["code"].values))
        if len(code_list) != 1:
            raise KabutobashiEntityError
        # 日時
        start_at = list(df["dt"])[0]
        end_at = list(df["dt"])[-1]

        required_columns = [
            "dt",
            "open",
            "close",
            "high",
            "low",
            "buy_signal",
            "sell_signal",
        ] + self.processed_columns()
        applied_df = self.apply(df=df)

        signal_df = self.signal(df=applied_df)
        params = self.parameterize(df_x=applied_df, df_p=signal_df)
        params.update({self.method_name: self._get_impact(df=signal_df, influence=influence, tail=tail)})
        return StockDataProcessed(
            code=code_list[0],
            df=signal_df,
            start_at=start_at,
            end_at=end_at,
            df_required_columns=required_columns,
            applied_method_name=self.method_name,
            parameters=params,
        )

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル分析の手法

        Args:
            df: 株の情報を含むDataFrame

        Returns:
            各分析手法の結果を付与したDataFrame
        """
        return self._apply(df=df.sort_values("dt"))

    @abstractmethod
    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("please implement your code")  # pragma: no cover

    def processed_columns(self) -> list:
        return self._processed_columns()

    @abstractmethod
    def _processed_columns(self) -> list:
        """
        各メソッドで計算時に出力されるカラムを明示する

        Returns:

        """
        raise NotImplementedError("please implement your code")  # pragma: no cover

    def signal(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル分析の手法の結果により、買いと売りのタイミングを計算する

        Args:
            df: 株の情報を含むDataFrame

        Returns:

        """
        return self._signal(df=df.sort_values("dt"))

    @abstractmethod
    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("please implement your code")  # pragma: no cover

    @staticmethod
    def _cross(_s: pd.Series, to_plus_name=None, to_minus_name=None) -> pd.DataFrame:
        """
        0を基準としてプラスかマイナスのどちらかに振れたかを判断する関数

        Args:
            _s: 対象のpd.Series
            to_plus_name: 上抜けた場合のカラムの名前
            to_minus_name: 下抜けた場合のカラムの名前
        """
        # shorten variable name
        col = "original"
        shifted = "shifted"

        # shiftしたDataFrameの作成
        shift_s = _s.shift(1)
        df = pd.DataFrame({col: _s, shifted: shift_s})

        # 正負が交差した点
        df = df.assign(
            is_cross=df.apply(lambda x: 1 if x[col] * x[shifted] < 0 else 0, axis=1),
            is_higher=df.apply(lambda x: 1 if x[col] > x[shifted] else 0, axis=1),
            is_lower=df.apply(lambda x: 1 if x[col] < x[shifted] else 0, axis=1),
        )

        # 上抜けか下抜けかを判断している
        df = df.assign(to_plus=df["is_cross"] * df["is_higher"], to_minus=df["is_cross"] * df["is_lower"])
        if to_plus_name is not None:
            df = df.rename(columns={"to_plus": to_plus_name})
        if to_minus_name is not None:
            df = df.rename(columns={"to_minus": to_minus_name})
        return df

    @staticmethod
    def _trend(_s: pd.Series) -> pd.Series:
        """
        ある系列_sのトレンドを計算する。
        差分のrolling_sumを返す
        """
        # shorten variable name
        col = "original"
        shifted = "shifted"

        # shiftしたDataFrameの作成
        shift_s = _s.shift(1)
        df = pd.DataFrame({col: _s, shifted: shift_s})
        df["diff"] = df["original"] - df["shifted"]
        df["diff_rolling_sum"] = df["diff"].rolling(5).sum()
        return df["diff_rolling_sum"]

    def parameterize(self, df_x: pd.DataFrame, df_p: pd.DataFrame) -> dict:
        return self._parameterize(df_x=df_x, df_p=df_p)

    @abstractmethod
    def _parameterize(self, df_x: pd.DataFrame, df_p: pd.DataFrame) -> dict:
        raise NotImplementedError("please implement your code")  # pragma: no cover

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
        columns = df.columns
        if "buy_signal" not in columns:
            return 0
        if "sell_signal" not in columns:
            return 0

        df["buy_impact"] = df["buy_signal"].ewm(span=influence).mean()
        df["sell_impact"] = df["sell_signal"].ewm(span=influence).mean()
        buy_impact_index = df["buy_impact"].iloc[-tail:].sum()
        sell_impact_index = df["sell_impact"].iloc[-tail:].sum()
        return round(buy_impact_index - sell_impact_index, 5)


class VisualizeMethod(ABC, BaseModel):
    def color_mapping(self) -> list:
        return self._color_mapping()

    @abstractmethod
    def _color_mapping(self) -> list:
        raise NotImplementedError("please implement your code")  # pragma: no cover

    def visualize_option(self) -> dict:
        return self._visualize_option()

    @abstractmethod
    def _visualize_option(self) -> dict:
        raise NotImplementedError("please implement your code")  # pragma: no cover

    @staticmethod
    def _add_ax_candlestick(ax, _df: pd.DataFrame):
        # datetime -> float
        time_series = mdates.date2num(_df["dt"])
        data = _df[["open", "high", "low", "close"]].values.T
        # data
        ohlc = np.vstack((time_series, data)).T
        candlestick_ohlc(ax, ohlc, width=0.7, colorup="g", colordown="r")

    def visualize(self, size_ratio: int, df: pd.DataFrame) -> StockDataVisualized:
        return StockDataVisualized(size_ratio=size_ratio, fig=self._visualize(size_ratio=size_ratio, df=df))

    def _visualize(self, size_ratio: int, df: pd.DataFrame):
        """
        Visualize Stock Data.

        Args:
            size_ratio: determine the size of the graph, default 2.

        Returns:
            Figure
        """

        def _n_rows() -> int:
            lower_nums = 1 if self.visualize_option()["position"] == "lower" else 0
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
        base_df = df[["dt", "open", "close", "high", "low"]]
        if n_rows == 1:
            base_axs = axs
        else:
            base_axs = axs[0]
        self._add_ax_candlestick(base_axs, base_df)

        ax_idx = 1
        # plots
        position = self.visualize_option()["position"]
        time_series = mdates.date2num(base_df["dt"])
        mapping = self.color_mapping()
        if position == "in":
            for m in mapping:
                df_key = m["df_key"]
                color = m["color"]
                label = m["label"]
                base_axs.plot(time_series, df[df_key], label=label)
            # display labels
            base_axs.legend(loc="best")
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


class Method(BaseModel):
    process_method: ProcessMethod
    visualize_method: Optional[VisualizeMethod]

    @staticmethod
    def of(process_method: ProcessMethod, visualize_method: Optional[VisualizeMethod]):
        return Method(process_method=process_method, visualize_method=visualize_method)
