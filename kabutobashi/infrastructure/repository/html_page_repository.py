from typing import NoReturn, Union

import requests  # type: ignore

from kabutobashi.domain.errors import KabutobashiPageError
from kabutobashi.domain.values import HtmlPage, IHtmlPageRepository, StockInfoHtmlPage, StockIpoHtmlPage, UserAgent

__all__ = [
    "HtmlPageBasicRepository",
    "StockInfoHtmlPageRepository",
    "StockIpoHtmlPageRepository",
    "StockInfoMultipleDaysMainHtmlPageRepository",
    "StockInfoMultipleDaysSubHtmlPageRepository",
]


class HtmlPageBasicRepository(IHtmlPageRepository):
    def __init__(self, url: str, page_type: str):
        self.url = url
        self.page_type = page_type

    @staticmethod
    def from_url(url: str, page_type: str) -> "HtmlPage":
        """
        requestsを使って、webからhtmlを取得する
        """
        user_agent = UserAgent.get_user_agent_header()
        r = requests.get(url, headers=user_agent)

        if r.status_code != 200:
            raise KabutobashiPageError(url=url)

        # 日本語に対応
        r.encoding = r.apparent_encoding
        return HtmlPage(html=r.text, page_type=page_type, url=url)

    def _html_page_read(self) -> HtmlPage:
        return self.from_url(url=self.url, page_type=self.page_type)

    def _read_hook(self, html_page: HtmlPage) -> HtmlPage:
        return html_page

    def _html_page_write(self, data: HtmlPage) -> NoReturn:
        pass


class StockInfoHtmlPageRepository(HtmlPageBasicRepository):
    def __init__(self, code: Union[int, str]):
        super().__init__(page_type="info", url=f"https://minkabu.jp/stock/{code}")
        self.code = code

    def _read_hook(self, html_page: HtmlPage) -> StockInfoHtmlPage:
        return StockInfoHtmlPage(code=self.code, html=html_page.html, page_type=self.page_type, url=self.url)


class StockIpoHtmlPageRepository(HtmlPageBasicRepository):
    def __init__(self, year: str):
        super().__init__(page_type="ipo", url=f"https://96ut.com/ipo/list.php?year={year}")
        self.year = year

    def _read_hook(self, html_page: HtmlPage) -> StockIpoHtmlPage:
        return StockIpoHtmlPage(html=html_page.html, page_type=self.page_type, url=self.url, year=self.year)


class StockInfoMultipleDaysMainHtmlPageRepository(HtmlPageBasicRepository):
    def __init__(self, code: Union[int, str]):
        super().__init__(page_type="info_multiple", url=f"https://minkabu.jp/stock/{code}/daily_bar")
        self.code = code


class StockInfoMultipleDaysSubHtmlPageRepository(HtmlPageBasicRepository):
    def __init__(self, code: Union[int, str]):
        super().__init__(page_type="info_multiple", url=f"https://minkabu.jp/stock/{code}/daily_valuation")
        self.code = code


class HtmlPageStorageRepository(IHtmlPageRepository):
    def _html_page_read(self) -> HtmlPage:
        pass

    def _html_page_write(self, data: HtmlPage) -> NoReturn:
        pass
