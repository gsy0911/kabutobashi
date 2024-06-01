import pandas as pd

from ..decorator import block

__all__ = ["ProcessBollingerBandsBlock"]


@block(block_name="process_bollinger_bands", series_required_columns=["close"])
class ProcessBollingerBandsBlock:
    series: pd.DataFrame
    band_term: int = 12
    continuity_term: int = 10

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(mean=df["close"].rolling(self.band_term).mean(), std=df["close"].rolling(self.band_term).std())
        df = df.assign(
            upper_1_sigma=df.apply(lambda x: x["mean"] + x["std"] * 1, axis=1),
            lower_1_sigma=df.apply(lambda x: x["mean"] - x["std"] * 1, axis=1),
            upper_2_sigma=df.apply(lambda x: x["mean"] + x["std"] * 2, axis=1),
            lower_2_sigma=df.apply(lambda x: x["mean"] - x["std"] * 2, axis=1),
            upper_3_sigma=df.apply(lambda x: x["mean"] + x["std"] * 3, axis=1),
            lower_3_sigma=df.apply(lambda x: x["mean"] - x["std"] * 3, axis=1),
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.assign(
            over_upper=df.apply(lambda x: 1 if x["close"] > x["upper_2_sigma"] else 0, axis=1),
            over_lower=df.apply(lambda x: 1 if x["close"] < x["lower_2_sigma"] else 0, axis=1),
            over_upper_continuity=lambda x: x["over_upper"].rolling(self.continuity_term).sum(),
            over_lower_continuity=lambda x: x["over_lower"].rolling(self.continuity_term).sum(),
        )

        df["bollinger_bands_buy_signal"] = df["over_upper"].apply(lambda x: 1 if x > 0 else 0)
        df["bollinger_bands_sell_signal"] = df["over_lower"].apply(lambda x: 1 if x > 0 else 0)
        return df

    def _process(self) -> pd.DataFrame:

        applied_df = self._apply(df=self.series)
        signal_df = self._signal(df=applied_df)
        required_columns = [
            "upper_1_sigma",
            "lower_1_sigma",
            "upper_2_sigma",
            "lower_2_sigma",
            "upper_3_sigma",
            "lower_3_sigma",
            "over_upper_continuity",
            "over_lower_continuity",
            "bollinger_bands_buy_signal",
            "bollinger_bands_sell_signal",
        ]
        return signal_df[required_columns]
