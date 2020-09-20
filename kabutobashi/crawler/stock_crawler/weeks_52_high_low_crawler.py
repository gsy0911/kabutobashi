from enum import Enum
from typing import Union

from bs4 import BeautifulSoup

from kabutobashi.crawler.crawler import Crawler
from kabutobashi.crawler.stock_crawler.weeks_52_high_low_page import (
    Week52HighLowStockPricePageTable
)
from kabutobashi.errors import PyStockMethodError


# 52週の高値・底値を取得する関数とURL
BASE_URL = "https://jp.tradingview.com/markets/stocks-japan"
WEEK_52_HIGH_PRICE_URL = f"{BASE_URL}/highs-and-lows-52wk-high/"
WEEK_52_LOW_PRICE_URL = f"{BASE_URL}/highs-and-lows-52wk-low/"
NEWLY_HIGH_PRICE_UPDATED = f"{BASE_URL}/highs-and-lows-ath/"
NEWLY_LOW_PRICE_UPDATED = f"{BASE_URL}/highs-and-lows-atl/"


class Week52CrawlType(Enum):
    HIGH = "high"
    LOW = "low"
    NEWLY_HIGH = "newly_high"
    NEWLY_LOW = "newly_low"


def get_52_weeks_high_low(crawl_objective: Union[str, Week52CrawlType]) -> dict:
    if crawl_objective == "high" or crawl_objective == Week52CrawlType.HIGH:
        target_url = WEEK_52_HIGH_PRICE_URL
    elif crawl_objective == "low" or crawl_objective == Week52CrawlType.LOW:
        target_url = WEEK_52_LOW_PRICE_URL
    elif crawl_objective == "newly_high" or crawl_objective == Week52CrawlType.NEWLY_HIGH:
        target_url = NEWLY_HIGH_PRICE_UPDATED
    elif crawl_objective == "newly_low" or crawl_objective == Week52CrawlType.NEWLY_LOW:
        target_url = NEWLY_LOW_PRICE_UPDATED
    else:
        raise PyStockMethodError("crawl_objective is not matched")

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
