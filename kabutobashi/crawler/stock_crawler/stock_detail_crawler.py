from typing import Union
from bs4 import BeautifulSoup

from kabutobashi.crawler.crawler import Crawler
from kabutobashi.crawler.stock_crawler.stock_detail_page import (
    StockBoard, StockDetail
)


def get_stock_detail(code: Union[str, int]) -> dict:
    """
    単一株の実行日時の詳細情報を取得する関数
    :params code: 取得したい銘柄コード
    :return:
    """
    url = f"https://minkabu.jp/stock/{code}"
    stock_detail_crawler = StockDetailCrawler()
    return stock_detail_crawler(url=url)


class StockDetailCrawler(Crawler):
    """
    インスタンスに付与したurlの株の情報を取得するCrawler
    """

    def __init__(self):
        super().__init__()

    def web_scraping(self, text: str) -> dict:
        """

        Args:
            text:
        """
        res = BeautifulSoup(text, 'lxml')
        stock_detail_dict = {}

        stock_board_tag = "ly_col ly_colsize_7 md_box ly_row ly_gutters"
        stock_board = res.find("div", {"class": stock_board_tag})
        # ページ上部の情報を取得
        sb = StockBoard(stock_board)
        stock_detail_dict.update(sb.get_info())

        # ページ中央の情報を取得
        stock_detail = res.find("div", {"class": "stock-detail"})
        sd = StockDetail(stock_detail)
        stock_detail_dict.update(sd.get_info())

        stock_detail_dict['crawl_datetime'] = self.get_crawl_datetime()
        return stock_detail_dict
