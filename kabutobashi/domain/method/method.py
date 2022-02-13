from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto

import pandas as pd


class MethodType(Enum):
    TECHNICAL_ANALYSIS = auto()
    PARAMETERIZE = auto()


@dataclass(frozen=True)  # type: ignore
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

    # 名前
    method_name: str
    # 種類:
    method_type: MethodType

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
        signal_df = stock_df.pipe(self._validate).pipe(self.method).pipe(self.signal)
        return signal_df

    def __str__(self) -> str:
        """
        分析方法の名前を返す
        """
        return self.method_name

    @staticmethod
    def _validate(df: pd.DataFrame) -> pd.DataFrame:
        from kabutobashi.domain.entity import StockDataSingleCode

        return StockDataSingleCode.of(df=df).df

    def method(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル分析の手法

        Args:
            df: 株の情報を含むDataFrame

        Returns:
            各分析手法の結果を付与したDataFrame
        """
        return self._method(df=df)

    @abstractmethod
    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        raise NotImplementedError("please implement your code")

    def color_mapping(self) -> list:
        return self._color_mapping()

    @abstractmethod
    def _color_mapping(self) -> list:
        raise NotImplementedError("please implement your code")

    def visualize_option(self) -> dict:
        return self._visualize_option()

    @abstractmethod
    def _visualize_option(self) -> dict:
        raise NotImplementedError("please implement your code")

    def processed_columns(self) -> list:
        return self._processed_columns()

    @abstractmethod
    def _processed_columns(self) -> list:
        """
        各メソッドで計算時に出力されるカラムを明示する

        Returns:

        """
        raise NotImplementedError("please implement your code")

    def signal(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        テクニカル分析の手法の結果により、買いと売りのタイミングを計算する

        Args:
            df: 株の情報を含むDataFrame

        Returns:

        """
        return self._signal(df=df)

    @abstractmethod
    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
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
        raise NotImplementedError("please implement your code")
