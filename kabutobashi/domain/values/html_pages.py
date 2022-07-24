from dataclasses import dataclass, field

import requests  # type: ignore
from bs4 import BeautifulSoup

from kabutobashi.domain.errors import KabutobashiPageError

from .user_agent import UserAgent


@dataclass(frozen=True)
class HtmlPage:
    """
    id: code & dt
    """

    html: str = field(repr=False)
    page_type: str
    url: str

    def __post_init__(self):
        assert self.page_type in ["info", "ipo", "weeks_52_high_low"]

    @staticmethod
    def from_url(url: str, page_type: str) -> "HtmlPage":
        """
        TODO repositoryを利用するように修正する
        requestsを使って、webからhtmlを取得する
        """
        user_agent = UserAgent.get_user_agent_header()
        r = requests.get(url, headers=user_agent)

        if r.status_code != 200:
            raise KabutobashiPageError(url=url)

        # 日本語に対応
        r.encoding = r.apparent_encoding
        return HtmlPage(html=r.text, page_type=page_type, url=url)

    def get_as_soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.html, features="lxml")


@dataclass(frozen=True)
class StockInfoHtmlPage(HtmlPage):
    code: str
    dt: str

    @staticmethod
    def of(code: str, dt: str) -> "StockInfoHtmlPage":
        url = f"https://minkabu.jp/stock/{code}"
        page_type = "info"
        html_page = HtmlPage.from_url(url=url, page_type=page_type)
        return StockInfoHtmlPage(page_type=page_type, code=code, dt=dt, html=html_page.html, url=url)


@dataclass(frozen=True)
class StockIpoHtmlPage(HtmlPage):
    year: str

    @staticmethod
    def of(year: str) -> "StockIpoHtmlPage":
        url = f"https://96ut.com/ipo/list.php?year={year}"
        page_type = "ipo"
        html_page = HtmlPage.from_url(url=url, page_type=page_type)
        return StockIpoHtmlPage(page_type=page_type, year=year, html=html_page.html, url=url)


@dataclass(frozen=True)
class StockWeeks52HighLowHtmlPage(HtmlPage):
    data_type: str
    dt: str

    def __post_init__(self):
        if self.data_type not in ["high", "low", "newly_high", "newly_low"]:
            raise KabutobashiPageError()

    @staticmethod
    def _url_suffix(data_type: str) -> str:
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

    @staticmethod
    def of(data_type: str, dt: str) -> "StockWeeks52HighLowHtmlPage":
        base_url = "https://jp.tradingview.com/markets/stocks-japan"
        url = f"{base_url}/{StockWeeks52HighLowHtmlPage._url_suffix(data_type=data_type)}"
        page_type = "weeks_52_high_low"
        html_page = HtmlPage.from_url(url=url, page_type=page_type)
        return StockWeeks52HighLowHtmlPage(
            page_type=page_type, data_type=data_type, html=html_page.html, url=url, dt=dt
        )
