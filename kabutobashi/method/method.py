from abc import abstractmethod
from kabutobashi.attributes import Field, StockDf
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from mplfinance.original_flavor import candlestick_ohlc
import logging


class MetaMethod(type):
    """
    値のget/setに関するメタクラス
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
    """
    MetaMethodを継承するクラス

    FieldClassとStockDfClassの値のget/setに関する操作をhookする
    """
    pass


class Method(AbstractMethod):
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
    stock_df = StockDf()

    def __init__(self, method_name: str, *, logger=None):
        """
        :params method_name: 分析手法の名前、__str__()で表示させる文字列
        """
        self.method_name = method_name
        if logger is None:
            self.logger = logging.getLogger()
            self.logger.setLevel(logging.INFO)
        else:
            self.logger = logger

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
        signal_df = stock_df.pipe(self.validate) \
            .pipe(self.method) \
            .pipe(self.signal)
        # 買い・売りのシグナルを算出する場合
        if "impact" in kwargs:
            return signal_df.pipe(self._get_impact, **kwargs)
        # それ以外は解析結果のdfを返す
        return signal_df

    def __str__(self) -> str:
        """
        分析方法の名前を返す
        """
        return self.method_name

    def validate(self, _df: pd.DataFrame) -> pd.DataFrame:
        self.stock_df = _df
        return self.stock_df

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

    def visualize(self, _df: pd.DataFrame):
        return self._visualize(_df=_df)

    def _visualize(self, _df: pd.DataFrame):
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
    def _cross(
            _s: pd.Series,
            to_plus_name=None,
            to_minus_name=None) -> pd.DataFrame:
        """
        0を基準としてプラスかマイナスのどちらかに振れたかを判断する関数
        
        Args:
            _s: 対象のpd.Series
            to_plus_name: 上抜けた場合のカラムの名前
            to_minus_name: 下抜けた場合のカラムの名前
        """
        # shorten vaiable name
        col = "original"
        shifted = "shifted"
        
        # shiftしたDataFrameの作成        
        shift_s = _s.shift(1)
        _df = pd.DataFrame({col: _s, shifted: shift_s})
        
        # 正負が交差した点
        _df = _df.assign(
            is_cross=_df.apply(lambda x: 1 if x[col] * x[shifted] < 0 else 0, axis=1),
            is_higher=_df.apply(lambda x: 1 if x[col] > x[shifted] else 0, axis=1),
            is_lower=_df.apply(lambda x: 1 if x[col] < x[shifted] else 0, axis=1)
        )

        # 上抜けか下抜けかを判断している
        _df = _df.assign(
            to_plus=_df['is_cross'] * _df['is_higher'],
            to_minus=_df['is_cross'] * _df['is_lower']
        )
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
        _df['diff'] = _df['original'] - _df['shifted']
        _df['diff_rolling_sum'] = _df['diff'].rolling(5).sum()
        return _df['diff_rolling_sum']

    @staticmethod
    def _get_impact(
            _df: pd.DataFrame,
            influence: int = 2,
            tail: int = 5,
            **kwargs) -> float:
        """
        売りと買いのシグナルの余波の合計値を返す。
        
        Args:
            _df: 
            influence:
            tail:
            
        Returns:
            [-1,1]の値をとる。-1: 売り、1: 買いを表す
        """
        _df['buy_impact'] = _df['buy_signal'].ewm(span=influence).mean()
        _df['sell_impact'] = _df['sell_signal'].ewm(span=influence).mean()
        buy_impact_index = _df['buy_impact'].iloc[-tail:].sum()
        sell_impact_index = _df['sell_impact'].iloc[-tail:].sum()
        return round(buy_impact_index - sell_impact_index, 5)

    @staticmethod
    def add_ax_candlestick(ax, _df: pd.DataFrame):
        # datetime -> float
        ohlc = np.vstack((mdates.date2num(_df.index), _df.values.T)).T
        candlestick_ohlc(ax, ohlc, width=0.7, colorup='g', colordown='r')
