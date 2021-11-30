from dataclasses import dataclass

import pandas as pd

from .method import Method, MethodType


@dataclass(frozen=True)
class Volatility(Method):
    """
    変動幅を計算する
    """

    method_name: str = "basic"
    method_type: MethodType = MethodType.PARAMETERIZE

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df_ = df.copy()
        df_["diff"] = -1
        # 正負が交差した点
        df_ = df_.join(self._cross(df_["diff"]))
        df_ = df_.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df_

    def _color_mapping(self) -> list:
        return []

    def _visualize_option(self) -> dict:
        return {"position": "-"}

    def _processed_columns(self) -> list:
        return []

    def _parameterize(self, df_x: pd.DataFrame, df_p: pd.DataFrame) -> dict:
        df = df_x.copy()
        df["volatility"] = (df["high"] - df["low"]) / df["close"]
        volatility = df["volatility"].mean()
        close_volatility = max(df["close"]) - min(df["close"]) / df["close"].median()
        return {"volatility": volatility, "close_volatility": close_volatility}
