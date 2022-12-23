from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import NoReturn, Union

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class HtmlPage:
    """
    id: code & dt
    """

    html: str = field(repr=False)
    page_type: str
    url: str

    def __post_init__(self):
        assert self.page_type in ["info", "info_multiple", "ipo", "weeks_52_high_low"]

    def get_as_soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.html, features="lxml")


class IHtmlPageRepository(ABC):
    def read(self) -> HtmlPage:
        html_page = self._html_page_read()
        return self._read_hook(html_page=html_page)

    def _read_hook(self, html_page: HtmlPage) -> HtmlPage:
        return html_page

    @abstractmethod
    def _html_page_read(self) -> HtmlPage:
        raise NotImplementedError()

    def write(self, data: HtmlPage) -> NoReturn:
        self._html_page_write(data=data)

    @abstractmethod
    def _html_page_write(self, data: HtmlPage) -> NoReturn:
        raise NotImplementedError()


@dataclass(frozen=True)
class StockInfoHtmlPage(HtmlPage):
    code: Union[int, str]
    dt: str


@dataclass(frozen=True)
class StockIpoHtmlPage(HtmlPage):
    year: str


@dataclass(frozen=True)
class StockWeeks52HighLowHtmlPage(HtmlPage):
    data_type: str
    dt: str


@dataclass(frozen=True)
class StockInfoMultipleDaysMainHtmlPage(HtmlPage):
    code: Union[int, str]


@dataclass(frozen=True)
class StockInfoMultipleDaysSubHtmlPage(HtmlPage):
    code: Union[int, str]


@dataclass(frozen=True)
class DecodedHtmlPage(ABC):
    """
    id: code & dt
    """

    def __post_init__(self):
        self._validate()

    @abstractmethod
    def _validate(self):
        raise NotImplementedError()


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

    def _validate(self):
        pass

    def is_delisting(self) -> bool:
        # 上場廃止の確認
        if self.open == "---" and self.high == "---" and self.low == "---":
            return True
        return False
