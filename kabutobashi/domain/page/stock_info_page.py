from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Union

from bs4 import BeautifulSoup

from kabutobashi.domain.entity import StockDataSingleDay
from kabutobashi.errors import KabutobashiPageError

from .page import Page, PageDecoder


@dataclass(frozen=True)
class StockInfoPage(Page):
    """

    Examples:
        >>> from kabutobashi import StockInfoPage
        >>> # get single page
        >>> sip = StockInfoPage(code="0001")
        >>> result = sip.get()
        >>> # get multiple page with multiprocessing
        >>> results = StockInfoPage.crawl_multiple(code_list=["0001", "0002", ...], max_workers=4)
    """

    code: Union[int, str]
    base_url: str = "https://minkabu.jp/stock/{code}"

    def url(self) -> str:
        return self.base_url.format(code=self.code)

    def _get(self) -> dict:
        soup = BeautifulSoup(self.get_url_text(url=self.url()), features="lxml")
        result = {}

        stock_board_tag = "ly_col ly_colsize_7 md_box ly_row ly_gutters"

        # ページ上部の情報を取得
        stock_board = soup.find("div", {"class": stock_board_tag})
        result.update(
            {
                "stock_label": PageDecoder(tag1="div", class1="stock_label").decode(bs=stock_board),
                "name": PageDecoder(tag1="p", class1="md_stockBoard_stockName").decode(bs=stock_board),
                "close": PageDecoder(tag1="div", class1="stock_price").decode(bs=stock_board),
                "date": PageDecoder(tag1="h2", class1="stock_label fsl").decode(bs=stock_board),
            }
        )

        # ページ中央の情報を取得
        stock_detail = soup.find("div", {"class": "stock-detail"})
        info = {}
        for li in stock_detail.find_all("li", {"class": "ly_vamd"}):
            info[li.find("dt").get_text()] = li.find("dd").get_text()
        result.update(
            {
                "industry_type": PageDecoder(tag1="div", class1="ly_content_wrapper size_ss").decode(bs=stock_detail),
                "open": info.get("始値", 0),
                "high": info.get("高値", 0),
                "low": info.get("安値", 0),
                "unit": info.get("単元株数", 0),
                "per": info.get("PER(調整後)", 0),
                "psr": info.get("PSR", 0),
                "pbr": info.get("PBR", 0),
                "volume": info.get("出来高", 0),
                "market_capitalization": info.get("時価総額", "-"),
                "issued_shares": info.get("発行済株数", "-"),
            }
        )
        return StockDataSingleDay.from_page_of(data=result).dumps()

    @staticmethod
    def crawl_single(code: Union[int, str]) -> dict:
        try:
            return StockInfoPage(code=code).get()
        except KabutobashiPageError:
            return {}

    @staticmethod
    def crawl_multiple(code_list: List[Union[int, str]], max_workers: int = 2) -> List[dict]:
        response_list = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            map_gen = executor.map(StockInfoPage.crawl_single, code_list)
            for response in map_gen:
                response_list.append(response)
        return response_list
