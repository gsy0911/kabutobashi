from abc import ABC, abstractmethod
from typing import List, NoReturn, Union

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field, field_validator


class RawHtmlPage(BaseModel):
    """
    Model: ValueObject
    JP: 変換対象HTML
    """

    html: str = Field(repr=False)
    page_type: str
    url: str

    @classmethod
    @field_validator("page_type")
    def _validate_page_type(cls, v):
        assert v in ["info", "info_multiple", "ipo"]

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


class RawHtmlPageStockInfo(RawHtmlPage):
    code: Union[int, str]


class RawHtmlPageStockIpo(RawHtmlPage):
    year: str
