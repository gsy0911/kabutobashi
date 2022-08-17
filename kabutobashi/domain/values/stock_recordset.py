from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from logging import INFO, getLogger
from typing import Generator, List, NoReturn, Optional, Set, Tuple

import pandas as pd

from kabutobashi.domain.entity import OPTIONAL_COL, REQUIRED_COL, StockBrand, StockRecord
from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.utilities import filter_weekday, get_past_n_days

logger = getLogger(__name__)
logger.setLevel(INFO)


@dataclass(frozen=True)
class StockRecordsetStatus:
    code: str
    is_delisting: bool = field(metadata={"jp": "更新停止"})
    contains_outlier: bool = field(metadata={"jp": "例外値を含む"})
    start_at: str = field(metadata={"jp": "収集開始日"})
    end_at: str = field(metadata={"jp": "最新日時"})


@dataclass(frozen=True)
class StockRecordset:
    """
    StockRecordset: root-entity
    """

    brand_set: Set[StockBrand] = field(repr=False)
    recordset: List[StockRecord] = field(repr=False)
    code_num: int = field(metadata={"jp": "銘柄数"})
    recordset_length: int = field(metadata={"jp": "データ数"})

    def __post_init__(self):
        if not self.recordset:
            raise KabutobashiEntityError("required stock_data")

    @staticmethod
    def of(df: pd.DataFrame) -> "StockRecordset":
        if "code" not in df.columns:
            raise KabutobashiEntityError
        recordset = []
        brand_set = set()
        df = df.dropna(subset=["code"])
        df.index.name = None
        # filter valid weekday
        date_unique_list = list(set(df["dt"]))
        dt_df = pd.DataFrame(filter_weekday(date_unique_list), columns=["dt"])
        df_joined = pd.merge(df, dt_df, on="dt", how="inner")

        for _, row in df_joined.iterrows():
            try:
                recordset.append(StockRecord.from_dict(dict(row)))
                brand_set.add(StockBrand.from_dict(data=dict(row)))
            except KabutobashiEntityError:
                logger.warning(f"error occurred at: {row}")
        return StockRecordset(
            brand_set=brand_set, recordset=recordset, code_num=len(brand_set), recordset_length=len(recordset)
        )

    def get_single_code_recordset_status(self) -> StockRecordsetStatus:

        if self.code_num > 1:
            raise KabutobashiEntityError

        code = list(self.brand_set)[0].code
        df = self._to_df(code=code)
        # 日時
        start_at = list(df["dt"])[0]
        end_at = list(df["dt"])[-1]

        # 日時が全て取得できているか
        date_list = get_past_n_days(current_date=end_at, n=len(df.index))
        if date_list[-1] != start_at:
            raise KabutobashiEntityError(
                f"some stock data lacks. start_at({start_at}) must be equal to {date_list[-1]}"
            )

        contains_outlier = any([v.is_outlier() for v in self.recordset])
        return StockRecordsetStatus(
            code=code,
            is_delisting=any([v.is_delisting for v in self.recordset]),
            contains_outlier=contains_outlier,
            start_at=start_at,
            end_at=end_at,
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
        if self.code_num > 1:
            raise KabutobashiEntityError
        df = self.to_df()
        df_length = len(df.index)
        if df_length < buy_sell_term_days + sliding_window:
            raise KabutobashiEntityError("入力されたDataFrameの長さがwindow幅よりも小さいです")
        loop = df_length - (buy_sell_term_days + sliding_window)
        for idx, i in enumerate(range(0, loop, step)):
            offset = i + sliding_window
            end = offset + buy_sell_term_days
            yield idx, df[i:offset], df[offset:end]

    def get_code_list(self) -> List[str]:
        return list([v.code for v in self.brand_set])

    def _to_df(self, code: Optional[str]) -> pd.DataFrame:
        df_brand = pd.DataFrame([v.to_dict() for v in self.brand_set])
        if code:
            df_brand = df_brand[df_brand["code"] == code]
        df_record = pd.DataFrame([v.to_dict() for v in self.recordset])
        df = pd.merge(left=df_brand, right=df_record, how="inner", on="code")

        df = df.convert_dtypes()
        # order by dt
        idx = pd.to_datetime(df["dt"]).sort_index()
        df.index = idx
        df = df.sort_index()
        return df

    def to_df(self, *, minimum=True, latest=False, code: Optional[str] = None):
        df = self._to_df(code=code)

        if latest:
            latest_dt = max(df["dt"])
            df = df[df["dt"] == latest_dt]

        if minimum:
            return df[REQUIRED_COL]
        else:
            return df[REQUIRED_COL + OPTIONAL_COL]

    def to_single_code(self, code: str) -> "StockRecordset":
        if type(code) is not str:
            raise KabutobashiEntityError("code must be type of `str`")
        return StockRecordset.of(df=self._to_df(code=code))

    def to_code_iterable(
        self,
        until: Optional[int] = None,
        *,
        skip_reit: bool = True,
        row_more_than: Optional[int] = 80,
        code_list: list = None,
    ) -> Generator[pd.DataFrame, None, None]:
        _count = 0
        df = self._to_df(code=None)

        if code_list:
            df = df[df["code"].isin(code_list)]
        if skip_reit:
            df = df[~(df["market"] == "東証REIT")]

        for code, df_ in df.groupby("code"):
            if row_more_than:
                if len(df_.index) < row_more_than:
                    continue

            # add counter if yield
            if until:
                if _count >= until:
                    return
            _count += 1

            yield df_


class IStockRecordsetRepository(ABC):
    def read(self) -> "StockRecordset":
        return self._stock_recordset_read()

    @abstractmethod
    def _stock_recordset_read(self) -> "StockRecordset":
        raise NotImplementedError()

    def write(self, data: StockRecordset) -> NoReturn:
        self._stock_recordset_write(data=data)

    @abstractmethod
    def _stock_recordset_write(self, data: StockRecordset) -> NoReturn:
        raise NotImplementedError()
