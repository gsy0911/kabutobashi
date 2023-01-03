from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field

from kabutobashi.domain.entity.util import _convert_float


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
class StockInfoMinkabuTopPage(DecodedHtmlPage):
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


@dataclass(frozen=True)
class StockIpo(DecodedHtmlPage):
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
        return StockIpo(
            code=data["code"],
            manager=data["主幹"],
            stock_listing_at=data["上場"],
            public_offering=_convert_float(data["公募"]),
            evaluation=data["評価"],
            initial_price=_convert_float(data["初値"]),
        )

    def to_dict(self) -> dict:
        return asdict(self)
