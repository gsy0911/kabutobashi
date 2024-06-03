from datetime import datetime

import jpholiday
import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block


@block(block_name="default_pre_process", series_required_columns=["open", "high", "low", "close", "code", "volume"])
class DefaultPreProcessBlock:
    for_analysis: bool
    series: pd.DataFrame

    def _process(self) -> pd.DataFrame:

        df = self.series
        # if self.for_analysis:
        required_cols = ["open", "high", "low", "close", "code", "volume"]
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        df = df[required_cols]

        df["dt"] = df.index
        df["passing"] = df["dt"].apply(lambda x: jpholiday.is_holiday(datetime.strptime(x, "%Y-%m-%d")))
        df = df[~df["passing"]]
        df = df.drop(["passing", "dt"], axis=1)
        return df
