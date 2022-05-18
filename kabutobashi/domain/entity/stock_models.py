from abc import ABCMeta, abstractmethod
from datetime import datetime
from typing import Generator, List, NoReturn, Optional, Set, Union

import pandas as pd
from pydantic import BaseModel, Field

from kabutobashi.domain.errors import KabutobashiEntityError

REQUIRED_COL = ["code", "open", "close", "high", "low", "volume", "per", "psr", "pbr", "dt"]
OPTIONAL_COL = ["name", "industry_type", "market", "unit"]


__all__ = [
    "StockBrand",
    "StockRecord",
    "StockRecordset",
    "StockIpo",
    "Weeks52HighLow",
    "IStockRecordsetRepository",
]


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

    id: int = Field(description="id")
    code: str = Field(description="銘柄コード")
    unit: int = Field(description="単位")
    market: str = Field(description="市場")
    name: str = Field(description="銘柄名")
    industry_type: str = Field(description="業種")
    market_capitalization: str = Field(description="時価総額")
    issued_shares: str = Field(description="発行済み株式")

    def __init__(
        self,
        id: Optional[int],
        code: str,
        unit: int,
        market: str,
        name: str,
        industry_type: str,
        market_capitalization: str,
        issued_shares: str,
    ):
        if id is None:
            id = 0
        super().__init__(
            id=id,
            code=code,
            unit=unit,
            market=market,
            name=name,
            industry_type=industry_type,
            market_capitalization=market_capitalization,
            issued_shares=issued_shares,
        )

    def dumps(self) -> dict:
        return self.dict()

    @staticmethod
    def loads(data: dict) -> "StockBrand":
        return StockBrand(
            id=data.get("id"),
            code=str(data["code"]),
            unit=_convert_int(data.get("unit", 0)),
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

    id: int = Field(description="id")
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

    def __init__(
        self,
        id: Optional[int],
        code: str,
        open: float,
        high: float,
        low: float,
        close: float,
        psr: float,
        per: float,
        pbr: float,
        volume: int,
        dt: str,
    ):

        if id is None:
            id = 0
        super().__init__(
            id=id,
            code=code,
            open=open,
            high=high,
            low=low,
            close=close,
            psr=psr,
            per=per,
            pbr=pbr,
            volume=volume,
            dt=dt,
        )

    @staticmethod
    def from_page_of(data: dict) -> "StockRecord":
        label_split = data["stock_label"].split("  ")
        try:
            return StockRecord(
                id=data.get("id"),
                code=label_split[0],
                open=_convert_float(data["open"]),
                high=_convert_float(data["high"]),
                low=_convert_float(data["low"]),
                close=_convert_float(data["close"]),
                psr=_convert_float(data["psr"]),
                per=_convert_float(data["per"]),
                pbr=_convert_float(data["pbr"]),
                volume=_convert_int(data["volume"]),
                dt=data["date"],
            )
        except Exception:
            return StockRecord(
                id=data.get("id"),
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
            id=data.get("id"),
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

    id: int = Field(description="id")
    code: str = Field(description="銘柄コード")
    manager: str = Field(description="主幹")
    stock_listing_at: str = Field(description="上場日")
    public_offering: float = Field(description="公募")
    evaluation: str = Field(description="評価")
    initial_price: float = Field(description="初値")

    def __init__(
        self,
        id: Optional[int],
        code: str,
        manager: str,
        stock_listing_at: str,
        public_offering: float,
        evaluation: str,
        initial_price: float,
    ):
        if id is None:
            id = 0
        super().__init__(
            id=id,
            code=code,
            manager=manager,
            stock_listing_at=stock_listing_at,
            public_offering=public_offering,
            evaluation=evaluation,
            initial_price=initial_price,
        )

    @staticmethod
    def loads(data: dict) -> "StockIpo":
        return StockIpo(
            id=data.get("id"),
            code=data["code"],
            manager=data["主幹"],
            stock_listing_at=data["上場"],
            public_offering=_convert_float(data["公募"]),
            evaluation=data["評価"],
            initial_price=_convert_float(data["初値"]),
        )

    def dumps(self) -> dict:
        return self.dict()


class Weeks52HighLow(BaseModel):
    """
    Weeks52HighLow: Entity

    52週高値・底値の値を保持するクラス
    """

    id: int = Field(description="id")
    code: str = Field(description="銘柄コード")
    brand_name: str = Field(description="銘柄名")
    close: float = Field(description="終値")
    buy_or_sell: str = Field(description="買い, 強い買い, 売り, 強い売り")
    volatility_ratio: float = Field(description="価格変動比")
    volatility_value: float = Field(description="価格変動値")
    dt: str = Field(description="日付")

    @staticmethod
    def from_page_of(data: dict) -> "Weeks52HighLow":
        buy = data["buy"]
        strong_buy = data["strong_buy"]
        sell = data["sell"]
        strong_sell = data["strong_sell"]

        return Weeks52HighLow(
            code=data["code"],
            brand_name=data["brand_name"],
            close=float(data["close"]),
            buy_or_sell=f"{buy}{strong_buy}{sell}{strong_sell}",
            volatility_ratio=_convert_float(data["volatility_ratio"]),
            volatility_value=_convert_float(data["volatility_value"]),
            dt="",
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
        df = df.dropna(subset=['code'])
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
