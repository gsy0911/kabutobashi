import pandas as pd

from ..decorator import block
from .abc_process_block import cross

__all__ = ["ProcessSmaBlock"]


@block(block_name="process_sma", series_required_columns=["close"])
class ProcessSmaBlock:
    series: pd.DataFrame
    short_term: int = 5
    medium_term: int = 21
    long_term: int = 70

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.assign(
            sma_short=df["close"].rolling(self.short_term).mean(),
            sma_medium=df["close"].rolling(self.medium_term).mean(),
            sma_long=df["close"].rolling(self.long_term).mean(),
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df["diff"] = df.apply(lambda x: x["sma_long"] - x["sma_short"], axis=1)
        # 正負が交差した点
        df = df.join(cross(df["diff"]))
        df = df.rename(columns={"to_plus": "sma_buy_signal", "to_minus": "sma_sell_signal"})
        return df

    def _process(self) -> pd.DataFrame:
        applied_df = self._apply(df=self.series)
        signal_df = self._signal(df=applied_df)
        return signal_df[["sma_short", "sma_medium", "sma_long", "sma_buy_signal", "sma_sell_signal"]]
