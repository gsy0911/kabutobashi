import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block


@block(block_name="default_pre_process", series_required_columns=["open", "high", "low", "close", "code", "volume"])
class DefaultPreProcessBlock:
    for_analysis: bool
    series: pd.DataFrame

    def _process(self) -> pd.DataFrame:

        df = self.series
        if self.for_analysis:
            required_cols = ["open", "high", "low", "close", "code", "volume"]
            if df is None:
                raise KabutobashiBlockSeriesIsNoneError()
            df = df[required_cols]
        return df
