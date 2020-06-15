from kabutobashi.crawler.crawler import Crawler
from kabutobashi.crawler.stock_crawler.weeks_52_high_low_page import (
    Week52HighLowStockPricePageTable
)
from bs4 import BeautifulSoup


# 52週の高値・底値を取得する関数とURL
BASE_URL = "https://jp.tradingview.com/markets/stocks-japan"
WEEK_52_HIGH_PRICE_URL = f"{BASE_URL}/highs-and-lows-52wk-high/"
WEEK_52_LOW_PRICE_URL = f"{BASE_URL}/highs-and-lows-52wk-low/"
NEWLY_HIGH_PRICE_UPDATED = f"{BASE_URL}/highs-and-lows-ath/"
NEWLY_LOW_PRICE_UPDATED = f"{BASE_URL}/highs-and-lows-atl/"


def get_52_weeks_high_low(crawl_objective: str) -> dict:
    target_url = None
    if crawl_objective == "high":
        target_url = WEEK_52_HIGH_PRICE_URL
    elif crawl_objective == "low":
        target_url = WEEK_52_LOW_PRICE_URL
    elif crawl_objective == "newly_high":
        target_url = NEWLY_HIGH_PRICE_UPDATED
    elif crawl_objective == "newly_low":
        target_url = NEWLY_LOW_PRICE_UPDATED
    else:
        raise Exception

    # instanceから直接__call__を呼び出して結果を出力
    crawler = Week52HighLowStockPriceCrawler()
    return crawler(url=target_url)


class Week52HighLowStockPriceCrawler(Crawler):
    """
    52週の高値・底値を取得するCrawler
    """

    def __init__(self):
        """
        :params crawl_objective: 取得対象を表す。
        """
        super().__init__()

    def web_scraping(self, text: str) -> dict:
        res = BeautifulSoup(text, 'lxml')

        content = res.find('tbody', class_="tv-data-table__tbody")
        page = Week52HighLowStockPricePageTable(content)
        return page.get_info()
