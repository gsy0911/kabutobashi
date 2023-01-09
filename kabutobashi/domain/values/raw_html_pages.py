from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, NoReturn, Union

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
    Model: Repository(for ValueObject, Interface)
    """

    def read(self) -> Union[RawHtmlPage, List[RawHtmlPage]]:
        html_page_list = self._html_page_read()
        return self._read_hook(html_page_list=html_page_list)

    def _read_hook(self, html_page_list: List[RawHtmlPage]) -> Union[RawHtmlPage, List[RawHtmlPage]]:
        return html_page_list

    @abstractmethod
    def _html_page_read(self) -> Union[RawHtmlPage, List[RawHtmlPage]]:
        raise NotImplementedError()  # pragma: no cover

    def write(self, data: RawHtmlPage) -> NoReturn:
        self._html_page_write(data=data)

    @abstractmethod
    def _html_page_write(self, data: RawHtmlPage) -> NoReturn:
        raise NotImplementedError()  # pragma: no cover


@dataclass(frozen=True)
class RawHtmlPageStockInfo(RawHtmlPage):
    code: Union[int, str]


@dataclass(frozen=True)
class RawHtmlPageStockIpo(RawHtmlPage):
    year: str


@dataclass(frozen=True)
class RawHtmlPageStockInfoMultipleDaysMain(RawHtmlPage):
    code: Union[int, str]


@dataclass(frozen=True)
class RawHtmlPageStockInfoMultipleDaysSub(RawHtmlPage):
    code: Union[int, str]
