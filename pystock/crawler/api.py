from pystock.crawler.crawler import Crawler
from typing import Union

# 単一銘柄の詳細情報を取得するクラス
from pystock.crawler.stock_crawler.stock_detail_crawler import (
    StockDetailCrawler
)

from pystock.crawler.stock_crawler.ipo_list_crawler import (
    IPOListCrawler
)

# 株価の情報を取得するクラス
from pystock.crawler.stock_crawler.stock_list_crawler import (
    StockBrandListCrawler,
    StockBrandOneIndustryListController,
    StockBrandAllIndustryController
)

from pystock.crawler.stock_crawler.stock_list_page import (
    OneRow
)

# OneRowのリストをDataFrameに変換する関数
convert_to_df = OneRow.convert_to_df


def get_beautifulsoup_result(url: str):
    crawler = Crawler()
    return crawler.get_beautifulsoup_result(url)


def get_stock_detail(code: Union[str, int]) -> dict:
    """
    単一株の実行日時の詳細情報を取得する関数
    :params code: 取得したい銘柄コード
    :return:
    """
    url = f"https://minkabu.jp/stock/{code}"
    stock_detail_crawler = StockDetailCrawler(url=url)
    return stock_detail_crawler.crawl()


def get_ipo_list_from_year(year: Union[str, int]) -> dict:
    """
    IPOのリストを取得する関数
    """
    base_url = "https://96ut.com/ipo/list.php"
    year_str = None
    if type(year) is int:
        year_str = str(year)
    else:
        year_str = year

    if year_str == "2020":
        # 実行年の場合
        url = base_url
    else:
        # 過去年の場合
        url = f"{base_url}?year={year}"
    ipo_list_crawler = IPOListCrawler(url=url)
    return ipo_list_crawler.crawl()

# def get_stock_brand_list_from_one_page(url: str) -> list:
#    """
#    単一のページから銘柄リストを取得する
#    """
#    stock_brand_list_crawler = StockBrandListCrawler(url=url)
#    stock_brand_list_crawler.crawl()
#    return stock_brand_list_crawler.get_info()


# def get_stock_brand_list_from_one_industry_type(url: str) -> list:
#    """
#    単一の業種の銘柄リストを取得する関数
#    """
#    stock_brand_list_crawler = StockBrandOneIndustryListController(
#        initial_url=url)
#    stock_brand_list_crawler.crawl()
#    return stock_brand_list_crawler.get_info()


# def get_stock_brand_list(base_url) -> list:
#    """
#    現在上場している銘柄リストを取得する関数
#    """
#    stock_brand_list_crawler = StockBrandAllIndustryController(
#        base_url=base_url)
#    stock_brand_list_crawler.crawl()
#    return stock_brand_list_crawler.get_info()
