from dataclasses import dataclass

import pandas as pd

from .method import Method


@dataclass(frozen=True)
class PsychoLogical(Method):
    """
    See Also:
        https://www.sevendata.co.jp/shihyou/technical/psycho.html
    """

    upper_threshold: float = 0.75
    lower_threshold: float = 0.25
    psycho_term: float = 12
    method_name: str = "psycho_logical"

    def _method(self, df: pd.DataFrame) -> pd.DataFrame:
        df["shift_close"] = df["close"].shift(1)
        df["diff"] = df.apply(lambda x: x["close"] - x["shift_close"], axis=1)

        df["is_raise"] = df["diff"].apply(lambda x: 1 if x > 0 else 0)

        df["psycho_sum"] = df["is_raise"].rolling(self.psycho_term).sum()
        df["psycho_line"] = df["psycho_sum"].apply(lambda x: x / self.psycho_term)

        df["bought_too_much"] = df["psycho_line"].apply(lambda x: 1 if x > self.upper_threshold else 0)
        df["sold_too_much"] = df["psycho_line"].apply(lambda x: 1 if x < self.lower_threshold else 0)
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df["buy_signal"] = df["sold_too_much"]
        df["sell_signal"] = df["bought_too_much"]
        return df

    def _color_mapping(self) -> list:
        return [
            {"df_key": "psycho_line", "color": "", "label": "psycho_line"},
        ]

    def _visualize_option(self) -> dict:
        return {"position": "lower"}

    def _processed_columns(self) -> list:
        return ["psycho_line", "bought_too_much", "sold_too_much"]

    def _parameterize(self) -> dict:
        return {}
