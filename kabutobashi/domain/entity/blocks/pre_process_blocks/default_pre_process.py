from datetime import datetime
from typing import Tuple

import jpholiday
import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesDtIsMissingError
from kabutobashi.utilities import convert_float, convert_int, get_working_days_between

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

    @staticmethod
    def _check_dt_requirements(df: pd.DataFrame):
        working_days = get_working_days_between(start_date=min(df["dt"]), end_date=max(df["dt"]))
        working_dt = pd.DataFrame(working_days, columns=["dt"])
        merged = pd.merge(df, working_dt, on="dt", how="outer")
        missing_df = merged[merged["name"].isnull()]
        if not missing_df.empty:
            raise KabutobashiBlockSeriesDtIsMissingError(code=str(list(set(df["code"]))[0]), dt=list(missing_df["dt"]))

    def _process(self) -> Tuple[pd.DataFrame, dict]:

        df = self.series
        # if self.for_analysis:
        #     required_cols = ["open", "high", "low", "close", "code", "volume"]
        #     if df is None:
        #         raise KabutobashiBlockSeriesIsNoneError()
        #     df = df[required_cols]

        columns = df.columns
        df["dt"] = df.index
        df = df.reset_index(drop=True)
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
        # check dt
        self._check_dt_requirements(df=df)
        # remove unused column
        df.index = df["dt"]

        # order by ASC
        df = df.sort_index()
        # fill `ffill` i.e. fill by previous value
        df["open"] = df.apply(lambda x: x["open"] if x["volume"] > 0 else None, axis=1)
        df["high"] = df.apply(lambda x: x["high"] if x["volume"] > 0 else None, axis=1)
        df["low"] = df.apply(lambda x: x["low"] if x["volume"] > 0 else None, axis=1)
        df["close"] = df.apply(lambda x: x["close"] if x["volume"] > 0 else None, axis=1)
        df = df.ffill()

        # remove unused columns
        df = df.drop(["passing"], axis=1)
        return df, {"dt": max(df["dt"])}
