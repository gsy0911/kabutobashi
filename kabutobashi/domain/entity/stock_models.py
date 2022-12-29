from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from kabutobashi.domain.errors import KabutobashiEntityError
from kabutobashi.domain.serialize import ICsvLineSerialize, IDictSerialize

from .util import _convert_float, _convert_int

REQUIRED_COL = ["code", "open", "close", "high", "low", "volume", "per", "psr", "pbr", "dt"]
OPTIONAL_COL = ["name", "industry_type", "market", "unit", "is_delisting"]


__all__ = ["StockBrand", "StockRecord", "StockIpo", "REQUIRED_COL", "OPTIONAL_COL"]


class StockBrand(BaseModel, IDictSerialize):
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
        # code may "100.0"
        code = code.split(".")[0]

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

    @staticmethod
    def from_dict(data: dict) -> "StockBrand":
        code = str(data["code"]).split(".")[0]

        return StockBrand(
            id=data.get("id"),
            code=code,
            unit=_convert_int(data.get("unit", 0)),
            market=data.get("market", ""),
            name=data.get("name", ""),
            industry_type=data.get("industry_type", ""),
            market_capitalization=data.get("market_capitalization", ""),
            issued_shares=data.get("issued_shares", ""),
        )

    def to_dict(self) -> dict:
        return self.dict()

    def is_reit(self) -> bool:
        return self.market == "東証REIT"

    def __eq__(self, other):
        if not isinstance(other, StockBrand):
            return False
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    class Config:
        orm_mode = True


class StockRecord(BaseModel, IDictSerialize, ICsvLineSerialize):
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
    is_delisting: bool = Field(description="上場廃止")
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
        is_delisting: bool,
        dt: str,
    ):

        if id is None:
            id = 0
        super().__init__(
            id=id,
            code=code,
            open=_convert_float(open),
            high=_convert_float(high),
            low=_convert_float(low),
            close=_convert_float(close),
            psr=_convert_float(psr),
            per=_convert_float(per),
            pbr=_convert_float(pbr),
            volume=_convert_float(volume),
            is_delisting=is_delisting,
            dt=dt,
        )

    @staticmethod
    def from_page_of(data: dict) -> "StockRecord":
        label_split = data["stock_label"].split("  ")
        try:
            return StockRecord(
                id=data.get("id"),
                code=label_split[0],
                open=data["open"],
                high=data["high"],
                low=data["low"],
                close=data["close"],
                psr=data["psr"],
                per=data["per"],
                pbr=data["pbr"],
                volume=data["volume"],
                is_delisting=data.get("is_delisting", False),
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
                is_delisting=False,
                dt="",
            )

    def is_outlier(self) -> bool:
        return self.open == 0 or self.high == 0 or self.low == 0 or self.close == 0

    def to_dict(self) -> dict:
        return self.dict()

    @staticmethod
    def from_dict(data: dict) -> "StockRecord":

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

        # code may "100.0"
        code = str(data["code"]).split(".")[0]
        return StockRecord(
            id=data.get("id"),
            code=code,
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            psr=data["psr"],
            per=data["per"],
            pbr=data["pbr"],
            volume=data["volume"],
            is_delisting=data.get("is_delisting", False),
            dt=dt,
        )

    @staticmethod
    def from_line(data: str):
        data = {sp_v[0]: sp_v[1] for v in data.split(",") if len(sp_v := v.split("=")) == 2}
        return StockRecord(**data)

    def to_line(self) -> str:
        data = [
            f"id={self.id}",
            f"code={self.code}",
            f"open={self.open}",
            f"high={self.high}",
            f"low={self.low}",
            f"close={self.close}",
            f"psr={self.psr}",
            f"per={self.per}",
            f"pbr={self.pbr}",
            f"volume={self.volume}",
            f"is_delisting={self.is_delisting}",
            f"dt={self.dt}",
        ]
        return ",".join(data)

    class Config:
        orm_mode = True


class StockIpo(BaseModel, IDictSerialize):
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
    def from_dict(data: dict) -> "StockIpo":
        return StockIpo(
            id=data.get("id"),
            code=data["code"],
            manager=data["主幹"],
            stock_listing_at=data["上場"],
            public_offering=_convert_float(data["公募"]),
            evaluation=data["評価"],
            initial_price=_convert_float(data["初値"]),
        )

    def to_dict(self) -> dict:
        return self.dict()

    class Config:
        orm_mode = True
