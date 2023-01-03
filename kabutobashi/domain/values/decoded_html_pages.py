from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field

from kabutobashi.utilities import convert_float
from kabutobashi.domain.serialize import IDictSerialize


@dataclass(frozen=True)
class DecodedHtmlPage(ABC):
    """
    Model: ValueObject
    JP: 変換済みHTML
    id: code & dt
    """

    def __post_init__(self):
        self._validate()

    @abstractmethod
    def _validate(self):
        raise NotImplementedError()  # pragma: no cover


@dataclass(frozen=True)
class StockInfoMinkabuTopPage(DecodedHtmlPage, IDictSerialize):
    code: str
    dt: str
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
    html: str = field(repr=False)

    def _validate(self):
        pass

    def is_delisting(self) -> bool:
        # 上場廃止の確認
        if self.open == "---" and self.high == "---" and self.low == "---":
            return True
        return False

    def to_dict(self) -> dict:
        data = asdict(self)
        del data["html"]
        return data

    @staticmethod
    def from_dict(data: dict) -> "StockInfoMinkabuTopPage":
        return StockInfoMinkabuTopPage(
            code=data["code"],
            dt=data["dt"],
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
            html=data["html"],
        )


@dataclass(frozen=True)
class StockIpo(DecodedHtmlPage, IDictSerialize):
    code: str = field(metadata={"jp": "銘柄コード"})
    manager: str = field(metadata={"jp": "主幹"})
    stock_listing_at: str = field(metadata={"jp": "上場日"})
    public_offering: float = field(metadata={"jp": "公募"})
    evaluation: str = field(metadata={"jp": "評価"})
    initial_price: float = field(metadata={"jp": "初値"})

    def _validate(self):
        pass

    @staticmethod
    def from_dict(data: dict) -> "StockIpo":
        manager = ""
        stock_listing_at = ""
        public_offering = 0
        evaluation = ""
        initial_price = 0
        if "主幹" in data:
            manager = data["主幹"]
        elif "manager" in data:
            manager = data["manager"]

        if "上場" in data:
            stock_listing_at = data["上場"]
        elif "stock_listing_at" in data:
            stock_listing_at = data["stock_listing_at"]

        if "公募" in data:
            public_offering = data["公募"]
        elif "public_offering" in data:
            public_offering = data["public_offering"]

        if "評価" in data:
            evaluation = data["評価"]
        elif "evaluation" in data:
            evaluation = data["evaluation"]

        if "初値" in data:
            initial_price = data["初値"]
        elif "initial_price" in data:
            initial_price = data["initial_price"]

        return StockIpo(
            code=data["code"],
            manager=manager,
            stock_listing_at=stock_listing_at,
            public_offering=convert_float(public_offering),
            evaluation=evaluation,
            initial_price=convert_float(initial_price),
        )

    def to_dict(self) -> dict:
        return asdict(self)
