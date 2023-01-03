from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import NoReturn, Union

from bs4 import BeautifulSoup

from kabutobashi.domain.entity.util import _convert_float


@dataclass(frozen=True)
class RawHtmlPage:
    """
    Model: ValueObject
    JP: 変換対象HTML
    """

    html: str = field(repr=False)
    page_type: str
    url: str

    def __post_init__(self):
        assert self.page_type in ["info", "info_multiple", "ipo", "weeks_52_high_low"]

    def get_as_soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.html, features="lxml")


class IHtmlPageRepository(ABC):
    def read(self) -> RawHtmlPage:
        html_page = self._html_page_read()
        return self._read_hook(html_page=html_page)

    def _read_hook(self, html_page: RawHtmlPage) -> RawHtmlPage:
        return html_page

    @abstractmethod
    def _html_page_read(self) -> RawHtmlPage:
        raise NotImplementedError()  # pragma: no cover

    def write(self, data: RawHtmlPage) -> NoReturn:
        self._html_page_write(data=data)

    @abstractmethod
    def _html_page_write(self, data: RawHtmlPage) -> NoReturn:
        raise NotImplementedError()  # pragma: no cover


@dataclass(frozen=True)
class StockInfoHtmlPage(RawHtmlPage):
    code: Union[int, str]


@dataclass(frozen=True)
class StockIpoHtmlPage(RawHtmlPage):
    year: str


@dataclass(frozen=True)
class StockInfoMultipleDaysMainHtmlPage(RawHtmlPage):
    code: Union[int, str]


@dataclass(frozen=True)
class StockInfoMultipleDaysSubHtmlPage(RawHtmlPage):
    code: Union[int, str]


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
