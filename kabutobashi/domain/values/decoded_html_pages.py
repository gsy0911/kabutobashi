from abc import ABC

from pydantic import BaseModel, Field, computed_field

from kabutobashi.utilities import convert_float

__all__ = [
    "DecodedHtmlPage",
    "DecodeHtmlPageStockIpo",
    "DecodeHtmlPageStockInfoMultipleDays",
    "DecodeHtmlPageStockInfoMinkabuTop",
]


class DecodedHtmlPage(ABC):
    """
    Model: ValueObject
    JP: 変換済みHTML
    id: code & dt
    """


class DecodeHtmlPageStockInfoMinkabuTop(BaseModel, DecodedHtmlPage):
    code: str
    dt: str
    name: str
    industry_type: str
    market: str
    open: str
    high: str
    low: str
    close: str
    unit: str
    per: str
    psr: str
    pbr: str
    volume: str
    market_capitalization: str
    issued_shares: str
    html: str = Field(repr=False)

    @computed_field
    @property
    def is_delisting(self) -> int:
        if self.open == "---" and self.high == "---" and self.low == "---":
            return True
        return False

    def to_dict(self) -> dict:
        return self.model_dump(exclude={"html"})

    @staticmethod
    def from_dict(data: dict) -> "DecodeHtmlPageStockInfoMinkabuTop":
        return DecodeHtmlPageStockInfoMinkabuTop(
            code=data["code"],
            dt=data["dt"],
            name=data["name"],
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            pbr=data["pbr"],
            per=data["per"],
            psr=data["psr"],
            unit=data["unit"],
            volume=data["volume"],
            market=data["market"],
            market_capitalization=data["market_capitalization"],
            industry_type=data["industry_type"],
            issued_shares=data["issued_shares"],
            html=data["html"],
        )


class DecodeHtmlPageStockInfoMultipleDays(BaseModel, DecodedHtmlPage):
    code: str
    dt: str
    open: str
    high: str
    low: str
    close: str
    per: str
    psr: str
    pbr: str
    volume: str
    html: str = Field(repr=False)

    def to_dict(self) -> dict:
        return self.model_dump(exclude={"html"})

    @staticmethod
    def from_dict(data: dict) -> "DecodeHtmlPageStockInfoMultipleDays":
        return DecodeHtmlPageStockInfoMultipleDays(
            code=data["code"],
            dt=data["dt"],
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            pbr=data["pbr"],
            per=data["per"],
            psr=data["psr"],
            volume=data["volume"],
            html="",
        )


class DecodeHtmlPageStockIpo(BaseModel, DecodedHtmlPage):
    code: str = Field(description="銘柄コード")
    name: str = Field(description="銘柄名")
    market: str = Field(description="市場")
    industry_type: str = Field(description="33業種区分")
    manager: str = Field(description="主幹")
    stock_listing_at: str = Field(description="上場日")
    public_offering: float = Field(description="公募")
    evaluation: str = Field(description="評価")
    initial_price: float = Field(description="初値")

    @staticmethod
    def from_dict(data: dict) -> "DecodeHtmlPageStockIpo":
        manager = ""
        name = ""
        market = ""
        stock_listing_at = ""
        industry_type = ""
        public_offering = 0
        evaluation = ""
        initial_price = 0
        if "主幹" in data:
            manager = data["主幹"]

        if "上場" in data:
            stock_listing_at = data["上場"]

        if "銘柄名" in data:
            name = data["銘柄名"]

        if "市場" in data:
            market = data["市場"]

        if "公募" in data:
            public_offering = data["公募"]

        if "評価" in data:
            evaluation = data["評価"]

        if "初値" in data:
            initial_price = data["初値"]

        return DecodeHtmlPageStockIpo(
            code=data["code"],
            name=name,
            market=market,
            industry_type=industry_type,
            manager=manager,
            stock_listing_at=stock_listing_at,
            public_offering=convert_float(public_offering),
            evaluation=evaluation,
            initial_price=convert_float(initial_price),
        )

    def to_dict(self) -> dict:
        return self.model_dump()
