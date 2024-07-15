import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockSeriesIsNoneError

from ..decorator import block


@block(
    block_name="parameterize_pct_change",
    series_required_columns=["close"],
)
class ParameterizePctChangeBlock:
    """
    変化率を計算する
    """

    series: pd.DataFrame

    def _process(self) -> dict:
        df = self.series
        if df is None:
            raise KabutobashiBlockSeriesIsNoneError()
        pct_05 = df["close"].pct_change(5).mean()
        pct_10 = df["close"].pct_change(10).mean()
        pct_20 = df["close"].pct_change(20).mean()
        pct_30 = df["close"].pct_change(30).mean()
        pct_40 = df["close"].pct_change(40).mean()
        return {
            "pct_05": pct_05,
            "pct_10": pct_10,
            "pct_20": pct_20,
            "pct_30": pct_30,
            "pct_40": pct_40,
            "dt": max(df.index.to_list()),
        }
