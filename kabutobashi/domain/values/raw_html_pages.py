from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import NoReturn, Union

from bs4 import BeautifulSoup


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
        assert self.page_type in ["info", "info_multiple", "ipo"]

    def get_as_soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.html, features="lxml")


class IHtmlPageRepository(ABC):
    """
    Model: Repository(for ValueObject)
    """

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
