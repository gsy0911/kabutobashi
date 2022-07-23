from dataclasses import dataclass
from functools import reduce
from logging import getLogger
from typing import List, Optional, Union

import requests  # type: ignore
from bs4 import BeautifulSoup

from kabutobashi.domain.values import StockPageHtml

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
        >>> from kabutobashi import StockPageHtml
        >>> # get single page
        >>> sph = StockPageHtml(url="https://minkabu.jp/stock/0001", code="0001", dt="2022-07-22", page_type="info")
        >>> result = StockInfoHtmlDecoder(page_html=sph).decode()
    """

    page_html: StockPageHtml

    def decode(self) -> dict:
        soup = self.page_html.get_as_soup()
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
                "dt": self.page_html.dt,
                "code": self.page_html.code,
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
