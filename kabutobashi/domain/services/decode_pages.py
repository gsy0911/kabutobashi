from dataclasses import dataclass
from functools import reduce
from logging import getLogger
from typing import List, Optional, Union

import requests  # type: ignore
from bs4 import BeautifulSoup

from kabutobashi.domain.values import StockInfoHtmlPage, StockIpoHtmlPage, StockWeeks52HighLowHtmlPage
from kabutobashi.domain.entity import StockIpo, Weeks52HighLow

logger = getLogger(__name__)


@dataclass(frozen=True)
class PageDecoder:
    tag1: Optional[str] = None
    class1: Optional[str] = None
    id1: Optional[str] = None
    default: str = ""

    def _decode(self, value):
        class1 = {"class": self.class1}

        set_value = None
        # tag1から取得
        if self.tag1 is not None:
            if class1["class"] is not None:
                set_value = value.find(self.tag1, self.class1)
            else:
                set_value = value.find(self.tag1)

        if set_value is None:
            return self.default

        # 文字列を置換して保持
        return self.replace(set_value.get_text())

    def decode(self, bs: BeautifulSoup) -> Union[str, List[str]]:
        return self._decode(value=bs)

    @staticmethod
    def replace(input_text: str) -> str:
        target_list = [" ", "\t", "\n", "\r", "円"]

        def remove_of(_input: str, target: str):
            return _input.replace(target, "")

        result = reduce(remove_of, target_list, input_text)
        return result.replace("\xa0", " ")


@dataclass(frozen=True)
class StockInfoHtmlDecoder:
    """

    Examples:
        >>> from kabutobashi import StockInfoHtmlPage
        >>> # get single page
        >>> page_html = StockInfoHtmlPage.of(code="0001", dt="2022-07-22")
        >>> result = StockInfoHtmlDecoder(page_html=page_html).decode()
    """

    html_page: StockInfoHtmlPage

    def decode(self) -> dict:
        soup = self.html_page.get_as_soup()
        result = {}

        stock_board_tag = "md_stockBoard"

        # ページ上部の情報を取得
        stock_board = soup.find("div", {"class": stock_board_tag})
        result.update(
            {
                "stock_label": PageDecoder(tag1="div", class1="stock_label").decode(bs=stock_board),
                "name": PageDecoder(tag1="p", class1="md_stockBoard_stockName").decode(bs=stock_board),
                "close": PageDecoder(tag1="div", class1="stock_price").decode(bs=stock_board),
                # "date": PageDecoder(tag1="h2", class1="stock_label fsl").decode(bs=stock_board),
            }
        )

        # ページ中央の情報を取得
        stock_detail = soup.find("div", {"id": "main"})
        info = {}
        for li in stock_detail.find_all("tr", {"class": "ly_vamd"}):
            info[li.find("th").get_text()] = li.find("td").get_text()
        result.update(
            {
                "dt": self.html_page.dt,
                "code": self.html_page.code,
                "industry_type": PageDecoder(tag1="div", class1="ly_content_wrapper size_ss").decode(bs=stock_detail),
                "open": info.get("始値", "0"),
                "high": info.get("高値", "0"),
                "low": info.get("安値", "0"),
                "unit": info.get("単元株数", "0"),
                "per": info.get("PER(調整後)", "0"),
                "psr": info.get("PSR", "0"),
                "pbr": info.get("PBR", "0"),
                "volume": info.get("出来高", "0"),
                "market_capitalization": info.get("時価総額", "---"),
                "issued_shares": info.get("発行済株数", "---"),
            }
        )
        return result


@dataclass(frozen=True)
class StockIpoHtmlDecoder:

    html_page: StockIpoHtmlPage

    def decode(self) -> dict:
        soup = self.html_page.get_as_soup()
        table_content = soup.find("div", {"class": "tablewrap"})
        table_thead = table_content.find("thead")
        # headの取得
        table_head_list = []
        for th in table_thead.find_all("th"):
            table_head_list.append(th.get_text())

        # bodyの取得
        table_tbody = table_content.find("tbody")
        whole_result = []
        for idx, tr in enumerate(table_tbody.find_all("tr")):
            table_body_dict = {}
            for header, td in zip(table_head_list, tr.find_all("td")):
                table_body_dict[header] = td.get_text().replace("\n", "")
            whole_result.append(StockIpo.loads(data=table_body_dict).dumps())
        return {"ipo_list": whole_result}


@dataclass(frozen=True)
class Weeks52HighLowHtmlDecoder:
    html_page: StockWeeks52HighLowHtmlPage

    def decode(self) -> dict:
        soup = self.html_page.get_as_soup()

        content = soup.find("body").find("tbody")
        table = content.find_all("tr")
        whole_result = []
        for t in table:
            buy_or_sell = ""

            for td in t.find_all("td"):
                if td.text in ["買い", "強い買い", "売り", "強い売り"]:
                    buy_or_sell = td.text
            data = {
                "code": PageDecoder(tag1="a").decode(bs=t),
                "brand_name": PageDecoder(tag1="span").decode(bs=t),
                "buy_or_sell": buy_or_sell,
                "dt": self.html_page.dt
            }
            whole_result.append(Weeks52HighLow.from_page_of(data=data).dumps())

        return {"weeks_52_high_low": whole_result}
