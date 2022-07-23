from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Generator, List, NoReturn, Optional, Set

import pandas as pd

from kabutobashi.domain.entity import OPTIONAL_COL, REQUIRED_COL, StockBrand, StockRecord
from kabutobashi.domain.errors import KabutobashiEntityError


@dataclass(frozen=True)
class StockRecordset:
    """
    StockRecordset: root-entity
    """

    brand_set: Set[StockBrand] = field(repr=False)
    recordset: List[StockRecord] = field(repr=False)

    def __post_init__(self):
        if not self.recordset:
            raise KabutobashiEntityError(f"required stock_data")

    @staticmethod
    def of(df: pd.DataFrame) -> "StockRecordset":
        if "code" not in df.columns:
            raise KabutobashiEntityError
        recordset = []
        brand_set = set()
        df = df.dropna(subset=["code"])
        for _, row in df.iterrows():
            recordset.append(StockRecord.loads(dict(row)))
            brand_set.add(StockBrand.loads(data=dict(row)))
        return StockRecordset(brand_set=brand_set, recordset=recordset)

    def get_code_list(self) -> List[str]:
        return list([v.code for v in self.brand_set])

    def _to_df(self, code: Optional[str]) -> pd.DataFrame:
        df_brand = pd.DataFrame([v.dumps() for v in self.brand_set])
        if code:
            df_brand = df_brand[df_brand["code"] == code]
        df_record = pd.DataFrame([v.dumps() for v in self.recordset])
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
            raise KabutobashiEntityError(f"code must be type of `str`")
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


class IStockRecordsetRepository(metaclass=ABCMeta):
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
