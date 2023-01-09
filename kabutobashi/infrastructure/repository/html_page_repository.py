from typing import List, NoReturn, Union

import requests  # type: ignore

from kabutobashi.domain.errors import KabutobashiPageError
from kabutobashi.domain.values import (
    IHtmlPageRepository,
    RawHtmlPage,
    RawHtmlPageStockInfo,
    RawHtmlPageStockInfoMultipleDaysMain,
    RawHtmlPageStockInfoMultipleDaysSub,
    RawHtmlPageStockIpo,
    UserAgent,
)

__all__ = [
    "HtmlPageBasicRepository",
    "StockInfoHtmlPageRepository",
    "StockIpoHtmlPageRepository",
    "StockInfoMultipleDaysHtmlPageRepository",
]


class HtmlPageBasicRepository(IHtmlPageRepository):
    """
    Model: Repository(Interface)
    """

    def __init__(self, urls: List[str], page_type: str):
        self.urls = urls
        self.page_type = page_type

    @staticmethod
    def from_url(url: str, page_type: str) -> "RawHtmlPage":
        user_agent = UserAgent.get_user_agent_header()
        r = requests.get(url, headers=user_agent)

        if r.status_code != 200:
            raise KabutobashiPageError(url=url)

        # 日本語に対応
        r.encoding = r.apparent_encoding
        return RawHtmlPage(html=r.text, page_type=page_type, url=url)

    def _html_page_read(self) -> List[RawHtmlPage]:
        return [self.from_url(url=url, page_type=self.page_type) for url in self.urls]

    def _read_hook(self, html_page: RawHtmlPage) -> RawHtmlPage:
        return html_page

    def _html_page_write(self, data: RawHtmlPage) -> NoReturn:
        pass


class StockInfoHtmlPageRepository(HtmlPageBasicRepository):
    """
    Model: Repository(Implemented)
    """

    def __init__(self, code: Union[int, str]):
        super().__init__(page_type="info", urls=[f"https://minkabu.jp/stock/{code}"])
        self.code = code

    def _read_hook(self, html_page_list: List[RawHtmlPage]) -> RawHtmlPageStockInfo:
        return RawHtmlPageStockInfo(
            code=self.code, html=html_page_list[0].html, page_type=self.page_type, url=self.urls[0]
        )


class StockIpoHtmlPageRepository(HtmlPageBasicRepository):
    """
    Model: Repository(Implemented)
    """

    def __init__(self, year: str):
        super().__init__(page_type="ipo", urls=[f"https://96ut.com/ipo/list.php?year={year}"])
        self.year = year

    def _read_hook(self, html_page_list: List[RawHtmlPage]) -> RawHtmlPageStockIpo:
        return RawHtmlPageStockIpo(
            html=html_page_list[0].html, page_type=self.page_type, url=self.urls[0], year=self.year
        )


class StockInfoMultipleDaysHtmlPageRepository(HtmlPageBasicRepository):
    """
    Model: Repository(Implemented)
    """

    def __init__(self, code: Union[int, str]):
        main_html = f"https://minkabu.jp/stock/{code}/daily_bar"
        sub_html = f"https://minkabu.jp/stock/{code}/daily_valuation"
        super().__init__(page_type="info_multiple", urls=[main_html, sub_html])
        self.code = code

    def _read_hook(
        self, html_page_list: List[RawHtmlPage]
    ) -> List[Union[RawHtmlPageStockInfoMultipleDaysMain, RawHtmlPageStockInfoMultipleDaysSub]]:
        return [
            RawHtmlPageStockInfoMultipleDaysMain(
                html=html_page_list[0].html, page_type=self.page_type, url=self.urls[0], code=self.code
            ),
            RawHtmlPageStockInfoMultipleDaysSub(
                html=html_page_list[1].html, page_type=self.page_type, url=self.urls[1], code=self.code
            ),
        ]
