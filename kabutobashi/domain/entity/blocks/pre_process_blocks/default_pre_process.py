from datetime import datetime

import jpholiday
import pandas as pd

from kabutobashi.utilities import convert_float, convert_int

from ..decorator import block


@block(
    block_name="default_pre_process",
    series_required_columns=["open", "high", "low", "close", "code", "volume"],
    series_required_columns_mode="all",
)
class DefaultPreProcessBlock:
    series: pd.DataFrame
    for_analysis: bool

    @staticmethod
    def _fix_dt(x: str) -> str:
        try:
            datetime.strptime(x, "%Y-%m-%d")
            return x
        except ValueError:
            pass

        try:
            dt = datetime.strptime(x, "%Y/%m/%d")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
        return ""

    @staticmethod
    def _is_holiday(x: str) -> bool:
        try:
            dt = datetime.strptime(x, "%Y-%m-%d")
            is_holiday = jpholiday.is_holiday(dt)
            return is_holiday
        except ValueError:
            return False

    def _process(self) -> pd.DataFrame:

        df = self.series
        # if self.for_analysis:
        #     required_cols = ["open", "high", "low", "close", "code", "volume"]
        #     if df is None:
        #         raise KabutobashiBlockSeriesIsNoneError()
        #     df = df[required_cols]

        columns = df.columns
        df["dt"] = df.index
        df["dt"] = df["dt"].apply(self._fix_dt)
        df["passing"] = df["dt"].apply(self._is_holiday)
        df["open"] = df["open"].apply(convert_float)
        df["high"] = df["high"].apply(convert_float)
        df["low"] = df["low"].apply(convert_float)
        df["close"] = df["close"].apply(convert_float)
        df["volume"] = df["volume"].apply(convert_int)
        if "pbr" in columns:
            df["pbr"] = df["pbr"].apply(convert_float)
        if "psr" in columns:
            df["psr"] = df["psr"].apply(convert_float)
        if "per" in columns:
            df["per"] = df["per"].apply(convert_float)
        df = df[~df["passing"]]
        df.index = df["dt"]
        df = df.drop(["passing"], axis=1)
        return df
