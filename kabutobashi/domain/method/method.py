from abc import ABCMeta, abstractmethod
from dataclasses import dataclass

import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc

from kabutobashi.domain.entity import StockDataProcessed, StockDataSingleCode


@dataclass(frozen=True)
class Method(metaclass=ABCMeta):
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

    # 株価を保持するDataFrame
    method_name: str

    def __call__(self, stock_df: pd.DataFrame, **kwargs):
        """
        各手法の時系列分析を行い、買いと売りのタイミングを付与

        Args:
            stock_df: 株の情報を含むDataFrame
            kwargs: {
                "impact": 売りと買いのシグナルを表示させるときに利用,
                "influence": get_impact()にて利用するパラメータ,
                "tail": get_impact()にて利用するパラメータ
            }
        """
        # 各手法指標となる値を計算し、買いと売りの指標を付与
        signal_df = stock_df.pipe(self.validate).pipe(self.method).pipe(self.signal)
        return signal_df

    def __str__(self) -> str:
        """
        分析方法の名前を返す
        """
        return self.method_name

    def validate(self, _df: pd.DataFrame) -> pd.DataFrame:
        return StockDataSingleCode.of(df=_df).data_df

    def method(self, _df: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル分析の手法

        Args:
            _df: 株の情報を含むDataFrame

        Returns:
            各分析手法の結果を付与したDataFrame
        """
        return self._method(_df=_df)

    @abstractmethod
    def _method(self, _df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("please implement your code")

    def process(self, _df: pd.DataFrame) -> StockDataProcessed:
        code_list = list(_df["code"].unique())
        if len(code_list) > 1:
            raise ValueError()
        base_df = _df[StockDataProcessed.REQUIRED_DF_COLUMNS]
        color_mapping = self._color_mapping()
        columns = ["dt", "buy_signal", "sell_signal"] + [v["df_key"] for v in color_mapping]

        return StockDataProcessed(
            code=code_list[0],
            base_df=base_df,
            processed_dfs=[
                {
                    "method": self.method_name,
                    "data": _df.pipe(self._method).pipe(self._signal).loc[:, columns],
                    "color_mapping": color_mapping,
                    "visualize_option": self._visualize_option(),
                }
            ],
        )

    @abstractmethod
    def _color_mapping(self) -> list:
        raise NotImplementedError("please implement your code")

    @abstractmethod
    def _visualize_option(self) -> dict:
        raise NotImplementedError("please implement your code")

    def signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル分析の手法の結果により、買いと売りのタイミングを計算する

        Args:
            _df: 株の情報を含むDataFrame

        Returns:

        """
        return self._signal(_df=_df)

    @abstractmethod
    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("please implement your code")

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
        _df = pd.DataFrame({col: _s, shifted: shift_s})

        # 正負が交差した点
        _df = _df.assign(
            is_cross=_df.apply(lambda x: 1 if x[col] * x[shifted] < 0 else 0, axis=1),
            is_higher=_df.apply(lambda x: 1 if x[col] > x[shifted] else 0, axis=1),
            is_lower=_df.apply(lambda x: 1 if x[col] < x[shifted] else 0, axis=1),
        )

        # 上抜けか下抜けかを判断している
        _df = _df.assign(to_plus=_df["is_cross"] * _df["is_higher"], to_minus=_df["is_cross"] * _df["is_lower"])
        if to_plus_name is not None:
            _df = _df.rename(columns={"to_plus": to_plus_name})
        if to_minus_name is not None:
            _df = _df.rename(columns={"to_minus": to_minus_name})
        return _df

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
        _df = pd.DataFrame({col: _s, shifted: shift_s})
        _df["diff"] = _df["original"] - _df["shifted"]
        _df["diff_rolling_sum"] = _df["diff"].rolling(5).sum()
        return _df["diff_rolling_sum"]

    @staticmethod
    def add_ax_candlestick(ax, _df: pd.DataFrame):
        # datetime -> float
        ohlc = np.vstack((mdates.date2num(_df.index), _df.values.T)).T
        candlestick_ohlc(ax, ohlc, width=0.7, colorup="g", colordown="r")
