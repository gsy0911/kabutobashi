import pandas as pd

from ..decorator import block
from .abc_process_block import cross


@block(block_name="process_momentum", series_required_columns=["close"])
class ProcessMomentumBlock:
    series: pd.DataFrame
    term: int = 12

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.assign(
            momentum=df["close"].shift(10),
        ).fillna(0)
        df = df.assign(sma_momentum=lambda x: x["momentum"].rolling(self.term).mean())
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.join(cross(df["sma_momentum"]))
        df = df.rename(columns={"to_plus": "momentum_buy_signal", "to_minus": "momentum_sell_signal"})
        return df

    def _process(self) -> pd.DataFrame:

        applied_df = self._apply(df=self.series)
        signal_df = self._signal(df=applied_df)
        required_columns = ["momentum", "sma_momentum", "momentum_buy_signal", "momentum_sell_signal"]
        return signal_df[required_columns]
