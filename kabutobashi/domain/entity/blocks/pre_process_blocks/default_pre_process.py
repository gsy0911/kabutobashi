import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block


@block(block_name="default_pre_process", pre_condition_block_name="extract_stock_info")
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
