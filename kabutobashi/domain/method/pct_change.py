from dataclasses import dataclass

import pandas as pd

from .method import Method, MethodType


@dataclass(frozen=True)
class PctChange(Method):
    """
    変化率を計算する
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
        pct_05 = df_x["close"].pct_change(5).mean()
        pct_10 = df_x["close"].pct_change(10).mean()
        pct_20 = df_x["close"].pct_change(20).mean()
        pct_30 = df_x["close"].pct_change(30).mean()
        pct_40 = df_x["close"].pct_change(40).mean()
        return {"pct_05": pct_05, "pct_10": pct_10, "pct_20": pct_20, "pct_30": pct_30, "pct_40": pct_40}
