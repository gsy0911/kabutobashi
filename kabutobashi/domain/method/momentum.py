from dataclasses import dataclass

import pandas as pd

from .method import Method


@dataclass(frozen=True)
class Momentum(Method):
    """
    See Also:
        https://www.sevendata.co.jp/shihyou/technical/momentum.html
    """

    term: int = 25
    method_name: str = "momentum"

    def _method(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.assign(
            momentum=_df["close"].shift(10), sma_momentum=lambda x: x["momentum"].rolling(self.term).mean()
        )
        return _df

    def _signal(self, _df: pd.DataFrame) -> pd.DataFrame:
        _df = _df.join(self._cross(_df["sma_momentum"]))
        _df = _df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return _df

    def _color_mapping(self) -> list:
        return [
            {"df_key": "momentum", "color": "", "label": "momentum"},
            {"df_key": "sma_momentum", "color": "", "label": "sma_momentum"},
        ]

    def _visualize_option(self) -> dict:
        return {"position": "lower"}
