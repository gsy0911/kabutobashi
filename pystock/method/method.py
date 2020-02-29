from pystock.attributes.attribute import Field, StockDf
import pandas as pd
import logging
# from matplotlib.dates import date2num
# import mpl_finance as mpf
import numpy as np


class MetaMethod(type):
    """
    値のget, setに関するメタクラス
    """
    def __new__(mcs, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, StockDf):
                value.name = key
                value.internal_name = '_' + key
            elif isinstance(value, Field):
                value.name = key
                value.internal_name = '_' + key
        cls = type.__new__(mcs, name, bases, class_dict)
        return cls


class AbstractMethod(object, metaclass=MetaMethod):
    pass


class Method(AbstractMethod):
    """
    usage
    sma = SMA()
    macd = MCAD()

    # get sma-based-analysis
    sma_df = stock_df.pipe(sma)

    # get macd-based-analysis
    macd_df = stock_df.pipe(macd)
    """
    # 株価を保持するDataFrame
    stock_df = StockDf()

    def __init__(self, *, logger=None):
        if logger is None:
            self.logger = logging.getLogger()
            self.logger.setLevel(logging.INFO)
        else:
            self.logger = logger

    def __call__(self, stock_df: pd.DataFrame, **kwds):
        """
        各手法の時系列分析を行い、買いと売りのタイミングを付与
        :params stock_df:
        """
        # 各手法指標となる値を計算し、買いと売りの指標を付与
        signal_df = stock_df.pipe(self.validate) \
            .pipe(self.method) \
            .pipe(self.signal)
        # figにする場合
        if "to_fig" in kwds:
            if kwds['to_fig']:
                return signal_df.pipe(self.visualize)
        # それ以外は解析結果のdfを返す
        return signal_df

    def __str__(self) -> str:
        return ""

    def validate(self, _df: pd.DataFrame) -> pd.DataFrame:
        self.stock_df = _df
        return self.stock_df

    def method(self, _df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("please implement your code")

    def signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("please implement your code")

    # def visualize(self, _df: pd.DataFrame):
    #     raise NotImplementedError("please implement your code")

    # @staticmethod
    # def add_ax_candlestick(ax, _df: pd.DataFrame):
    #     # datetime -> float
    #     ohlc = np.vstack((date2num(_df.index), _df.values.T)).T
    #     mpf.candlestick_ohlc(ax, ohlc, width=0.7, colorup='g', colordown='r')

    @staticmethod
    def cross(_s: pd.Series) -> pd.Series:
        shift_s = _s.shift(1)
        _df = pd.DataFrame({"original": _s, "shifted": shift_s})
        # shorten vaiable name
        col = "original"
        shifted = "shifted"
        # 正負が交差した点
        _df = _df.assign(
            is_cross=_df.apply(lambda x: 1 if x[col] * x[shifted] < 0 else 0, axis=1),
            is_higher=_df.apply(lambda x: 1 if x[col] > x[shifted] else 0, axis=1),
            is_lower=_df.apply(lambda x: 1 if x[col] < x[shifted] else 0, axis=1)
        )

        _df = _df.assign(
            to_plus=_df['is_cross'] * _df['is_higher'],
            to_minus=_df['is_cross'] * _df['is_lower']
        )
        return _df
