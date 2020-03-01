from pystock.crawler.crawler import Crawler
from pystock.crawler.stock_crawler.stock_detail_page import StockBoard, StockDetail


class StockDetailCrawler(Crawler):
    """
    インスタンスに付与したurlの株の情報を取得するCrawler
    """

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def crawl(self) -> dict:
        """
        urlをcrawlし、取得した結果を返す関数
        """
        bs2 = self.get_beautifulsoup_result(self.url)

        stock_detail_dict = {}

        stock_board = bs2.find("div", {"class": "ly_col ly_colsize_7 md_box ly_row ly_gutters"})
        # ページ上部の情報を取得
        sb = StockBoard(stock_board)
        stock_detail_dict.update(sb.get_info())

        # ページ中央の情報を取得
        stock_detail = bs2.find("div", {"class": "stock-detail"})
        sd = StockDetail(stock_detail)
        stock_detail_dict.update(sd.get_info())

        stock_detail_dict['crawl_datetime'] = self.get_crawl_datetime()
        return stock_detail_dict
