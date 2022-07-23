from dataclasses import dataclass, field
from typing import Generator, Tuple

import pandas as pd

from kabutobashi.domain.errors import KabutobashiEntityError

from .stock_recordset import StockRecordset

__all__ = ["StockDataSingleCode"]


@dataclass(frozen=True)
class StockDataSingleCode:
    """
    StockDataSingleCode: ValueObject

    Examples:
        >>> import kabutobashi as kb
        >>> import pandas as pd
        >>> data_list = []
        >>> records = kb.example()
        >>> parameterize_methods = kb.methods + [kb.basic, kb.pct_change, kb.volatility]
        >>>
        >>> for df in records.to_code_iterable(until=1, row_more_than=80):
        >>>     sdsc = StockDataSingleCode.of(df=df)
        >>>     for idx, df_x, df_y in sdsc.sliding_split():
        >>>         df_params = kb.StockDataProcessedBySingleMethod.of(df=df_x, methods=parameterize_methods)
        >>>         # diff:= df_y.last - df_x.last
        >>>         start = list(df_x["close"])[-1]
        >>>         end = list(df_y["close"])[-1]
        >>>         diff = end - start
        >>>         d = df_params.get_parameters()
        >>>         d.update({"diff": diff})
        >>>         data_list.append(d)
        >>>  data_for_ml = pd.DataFrame(data_list)
    """

    code: str = field(metadata={"jp": "銘柄コード"})
    stop_updating: bool = field(metadata={"jp": "更新停止"})
    contains_outlier: bool = field(metadata={"jp": "例外値を含む"})
    stock_recordset: StockRecordset = field(metadata={"jp": "株データ"})
    len_: int = field(metadata={"jp": "データ数"})

    def __post_init__(self):
        self._code_constraint_check(stock_recordset=self.stock_recordset)

    @staticmethod
    def _code_constraint_check(stock_recordset: StockRecordset):
        brands = stock_recordset.get_code_list()
        if len(brands) > 1:
            raise KabutobashiEntityError("multiple code")
        elif len(brands) == 0:
            raise KabutobashiEntityError("no code")
        code_records = list(set([v.code for v in stock_recordset.recordset]))
        if len(code_records) > 1:
            raise KabutobashiEntityError("multiple code")
        elif len(code_records) == 0:
            raise KabutobashiEntityError("no code")

    @staticmethod
    def of(df: pd.DataFrame):
        recordset = StockRecordset.of(df=df)

        # codeの確認
        StockDataSingleCode._code_constraint_check(stock_recordset=recordset)
        code = recordset.get_code_list()[0]
        return StockDataSingleCode(
            code=code,
            stock_recordset=recordset,
            stop_updating=StockDataSingleCode._check_recent_update(df=df),
            contains_outlier=any([v.is_outlier() for v in recordset.recordset]),
            len_=len(recordset.recordset),
        )

    @staticmethod
    def _check_recent_update(df: pd.DataFrame) -> bool:
        """
        直近の更新が止まっているかどうか
        """
        return (
            (len(df["open"].tail(10).unique()) == 1)
            or (len(df["high"].tail(10).unique()) == 1)
            or (len(df["low"].tail(10).unique()) == 1)
            or (len(df["close"].tail(10).unique()) == 1)
        )

    def sliding_split(
        self, *, buy_sell_term_days: int = 5, sliding_window: int = 60, step: int = 3
    ) -> Generator[Tuple[int, pd.DataFrame, pd.DataFrame], None, None]:
        """
        単一の銘柄に関してwindow幅を ``sliding_window`` 日として、
        保持しているデータの期間の間をslidingしていく関数。

        Args:
            buy_sell_term_days: この日数後までデータを切り出す。
            sliding_window: slidingしていくwindow幅
            step: windowsをずらしていく期間

        Returns:
            idx: 切り出された番号。
            df_for_x: 特徴量を計算するためのDataFrame。
            df_for_y: ``buy_sell_term_days`` 後のDataFrameを返す。値動きを追うため。
        """
        df = self.to_df()
        df_length = len(df.index)
        if df_length < buy_sell_term_days + sliding_window:
            raise KabutobashiEntityError("入力されたDataFrameの長さがwindow幅よりも小さいです")
        loop = df_length - (buy_sell_term_days + sliding_window)
        for idx, i in enumerate(range(0, loop, step)):
            offset = i + sliding_window
            end = offset + buy_sell_term_days
            yield idx, df[i:offset], df[offset:end]

    def to_df(self, minimum=True, latest=False) -> pd.DataFrame:
        return self.stock_recordset.to_df(minimum=minimum, latest=latest)

    def __len__(self):
        return self.len_
