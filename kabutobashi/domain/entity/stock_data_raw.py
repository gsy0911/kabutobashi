from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Generator, List, NoReturn, Optional, Set, Tuple, Union

import pandas as pd
from pydantic import BaseModel, Field

from kabutobashi.domain.errors import KabutobashiEntityError

REQUIRED_COL = ["code", "open", "close", "high", "low", "volume", "per", "psr", "pbr", "dt"]
OPTIONAL_COL = ["name", "industry_type", "market", "unit"]


__all__ = ["StockBrand", "StockRecord", "StockRecordset", "StockDataSingleCode", "IStockRecordsetRepository"]


def _replace(input_value: str) -> str:
    if input_value == "-":
        return "0"
    return input_value.replace("---", "0").replace("円", "").replace("株", "").replace("倍", "").replace(",", "")


def _convert_float(input_value: Union[str, float, int]) -> float:
    if type(input_value) is float or type(input_value) is int:
        return float(input_value)
    elif type(input_value) is str:
        try:
            return float(_replace(input_value=input_value))
        except ValueError as e:
            raise KabutobashiEntityError(f"floatに変換できる値ではありません。{e}")
    raise KabutobashiEntityError(f"floatに変換できる値ではありません。")


def _convert_int(input_value: Union[str, float, int]) -> int:
    if type(input_value) == float or type(input_value) == int:
        return int(input_value)
    elif type(input_value) is str:
        try:
            return int(_replace(input_value=input_value))
        except ValueError as e:
            raise KabutobashiEntityError(f"floatに変換できる値ではありません。{e}")
    raise KabutobashiEntityError(f"floatに変換できる値ではありません。")


class StockBrand(BaseModel):
    """
    StockBrand: entity
    """

    code: str = Field(description="銘柄コード")
    unit: int = Field(description="単位")
    market: str = Field(description="市場")
    name: str = Field(description="銘柄名")
    industry_type: str = Field(description="業種")
    market_capitalization: str = Field(description="時価総額")
    issued_shares: str = Field(description="発行済み株式")

    def dumps(self) -> dict:
        return self.dict()

    @staticmethod
    def loads(data: dict) -> "StockBrand":
        return StockBrand(
            code=str(data["code"]),
            unit=_convert_int(data["unit"]),
            market=data.get("market", ""),
            name=data.get("name", ""),
            industry_type=data.get("industry_type", ""),
            market_capitalization=data.get("market_capitalization", ""),
            issued_shares=data.get("issued_shares", ""),
        )

    def is_reit(self) -> bool:
        return self.market == "東証REIT"

    def __eq__(self, other):
        if not isinstance(other, StockBrand):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)


class StockRecord(BaseModel):
    """
    StockRecord: entity
    """

    # TODO implements id_: str
    code: str = Field(description="銘柄コード")
    open: float = Field(description="始値")
    high: float = Field(description="高値")
    low: float = Field(description="底値")
    close: float = Field(description="終値")
    psr: float = Field(description="PSR")
    per: float = Field(description="PER")
    pbr: float = Field(description="PBR")
    volume: int = Field(description="出来高")
    dt: str = Field(description="日付")

    @staticmethod
    def from_page_of(data: dict) -> "StockRecord":
        label_split = data["stock_label"].split("  ")
        try:
            return StockRecord(
                code=label_split[0],
                open=_replace(data["open"]),
                high=_replace(data["high"]),
                low=_replace(data["low"]),
                close=_replace(data["close"]),
                unit=_replace(data["unit"]),
                psr=_replace(data["psr"]),
                per=_replace(data["per"]),
                pbr=_replace(data["pbr"]),
                volume=_replace(data["volume"]),
                dt=data["date"],
            )
        except Exception:
            return StockRecord(
                code="",
                open=0,
                high=0,
                low=0,
                close=0,
                psr=0,
                per=0,
                pbr=0,
                volume=0,
                dt="",
            )

    def is_outlier(self) -> bool:
        return self.open == 0 or self.high == 0 or self.low == 0 or self.close == 0

    def dumps(self) -> dict:
        return self.dict()

    @staticmethod
    def loads(data: dict) -> "StockRecord":

        data_date = data.get("date")
        data_dt = data.get("dt")
        data_crawl_datetime = data.get("crawl_datetime")

        if data_date and data_dt and data_crawl_datetime:
            raise KabutobashiEntityError("日付のカラム[dt, date, crawl_datetime]のいずれかしか選べません")
        if data_date:
            dt = data_date
        elif data_dt:
            dt = data_dt
        elif data_crawl_datetime:
            dt = datetime.fromisoformat(data_crawl_datetime).strftime("%Y-%m-%d")
        else:
            raise KabutobashiEntityError("日付のカラム[dt, date, crawl_datetime]のいずれかが存在しません")

        return StockRecord(
            code=str(data["code"]),
            open=_convert_float(data["open"]),
            high=_convert_float(data["high"]),
            low=_convert_float(data["low"]),
            close=_convert_float(data["close"]),
            psr=_convert_float(data["psr"]),
            per=_convert_float(data["per"]),
            pbr=_convert_float(data["pbr"]),
            volume=data["volume"],
            dt=dt,
        )


class StockIpo(BaseModel):
    """
    まだ取り込んでない値など

    '想定(仮条件)': '1,920(1,900-1,920)',
    '吸収金額': '75.6億',
    '(騰落率)損益': '(+1.1%)+2,100円00001',

    """

    code: int
    manager: str = Field(description="主幹")
    stock_listing_at: str = Field(description="上場日")
    public_offering: float = Field(description="公募")
    evaluation: str = Field(description="評価")
    initial_price: float = Field(description="初値")

    @staticmethod
    def loads(data: dict) -> "StockIpo":
        return StockIpo(
            code=data["code"],
            manager=data["主幹"],
            stock_listing_at=data["上場"],
            public_offering=_convert_float(data["公募"]),
            evaluation=data["評価"],
            initial_price=_convert_float(data["初値"]),
        )

    def dumps(self) -> dict:
        return self.dict()


class StockRecordset(BaseModel):
    """
    StockRecordset: root-entity
    """

    brand_set: Set[StockBrand] = Field(repr=False)
    recordset: List[StockRecord] = Field(repr=False)

    def __post_init__(self):
        if not self.recordset:
            raise KabutobashiEntityError(f"required stock_data")

    @staticmethod
    def of(df: pd.DataFrame) -> "StockRecordset":
        recordset = []
        brand_set = set()
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

    def to_single_code(self, code: str) -> "StockDataSingleCode":
        if type(code) is not str:
            raise KabutobashiEntityError(f"code must be type of `str`")
        return StockDataSingleCode.of(df=self._to_df(code=code))

    def to_code_iterable(
        self,
        until: Optional[int] = None,
        *,
        skip_reit: bool = True,
        row_more_than: Optional[int] = 80,
        code_list: list = None,
    ) -> Generator["StockDataSingleCode", None, None]:
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

            # create sdsc
            sdsc = StockDataSingleCode.of(df=df_)
            if sdsc.stop_updating:
                continue
            if sdsc.contains_outlier:
                continue

            # add counter if yield
            if until:
                if _count >= until:
                    return
            _count += 1

            yield sdsc


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


@dataclass(frozen=True)
class StockDataSingleCode:
    """
    StockDataSingleCode: ValueObject

    Examples:
        >>> import kabutobashi as kb
        >>> import pandas as pd
        >>> data_list = []
        >>> sdmc = kb.example()
        >>> parameterize_methods = kb.methods + [kb.basic, kb.pct_change, kb.volatility]
        >>> for sdsc in sdmc.to_code_iterable(until=1, row_more_than=80):
        >>>     code = sdsc.code
        >>>     print(code)
        >>>     for idx, df_x, df_y in sdsc.sliding_split():
        >>>         df_params = kb.StockDataAnalyzedByMultipleMethod.of(df=df_x, methods=parameterize_methods)
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
