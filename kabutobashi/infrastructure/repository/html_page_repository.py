from typing import NoReturn, Union

import requests

from kabutobashi.domain.errors import KabutobashiPageError
from kabutobashi.domain.values import (
    HtmlPage,
    IHtmlPageRepository,
    StockInfoHtmlPage,
    StockIpoHtmlPage,
    StockWeeks52HighLowHtmlPage,
    UserAgent,
)

__all__ = [
    "HtmlPageBasicRepository",
    "StockInfoHtmlPageRepository",
    "StockIpoHtmlPageRepository",
    "StockWeeks52HighLowHtmlPageRepository",
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
    def __init__(self, code: Union[int, str], dt: str):
        super().__init__(page_type="info", url=f"https://minkabu.jp/stock/{code}")
        self.code = code
        self.dt = dt

    def _read_hook(self, html_page: HtmlPage) -> StockInfoHtmlPage:
        return StockInfoHtmlPage(
            code=self.code, html=html_page.html, dt=self.dt, page_type=self.page_type, url=self.url
        )


class StockIpoHtmlPageRepository(HtmlPageBasicRepository):
    def __init__(self, year: str):
        super().__init__(page_type="ipo", url=f"https://96ut.com/ipo/list.php?year={year}")
        self.year = year

    def _read_hook(self, html_page: HtmlPage) -> StockIpoHtmlPage:
        return StockIpoHtmlPage(html=html_page.html, page_type=self.page_type, url=self.url, year=self.year)


class StockWeeks52HighLowHtmlPageRepository(HtmlPageBasicRepository):
    @staticmethod
    def _url_suffix(data_type: str) -> str:
        if data_type not in ["high", "low", "newly_high", "newly_low"]:
            raise KabutobashiPageError()

        # 52週の高値・底値を取得する関数とURL
        if data_type == "high":
            return "highs-and-lows-52wk-high"
        elif data_type == "low":
            return "highs-and-lows-52wk-low"
        elif data_type == "newly_high":
            return "highs-and-lows-ath"
        elif data_type == "newly_low":
            return "highs-and-lows-atl"

        raise KabutobashiPageError()

    def __init__(self, data_type: str, dt: str):
        base_url = "https://jp.tradingview.com/markets/stocks-japan"
        url = f"{base_url}/{StockWeeks52HighLowHtmlPageRepository._url_suffix(data_type=data_type)}"
        super().__init__(page_type="weeks_52_high_low", url=url)
        self.data_type = data_type
        self.dt = dt

    def _read_hook(self, html_page: HtmlPage) -> StockWeeks52HighLowHtmlPage:
        return StockWeeks52HighLowHtmlPage(
            html=html_page.html, page_type=self.page_type, url=self.url, data_type=self.data_type, dt=self.dt
        )


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
