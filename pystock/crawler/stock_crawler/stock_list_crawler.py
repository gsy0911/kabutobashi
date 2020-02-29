from pystock.crawler.crawler import Crawler
from pystock.crawler.stock_crawler.stock_list_page import (
    LinkContent, OneRow
)
from typing import Union
from time import sleep


class StockBrandAllIndustryController:
    """
    指定された業種の上場銘柄を取得するクラス。
    """
    numbers = list(range(34))

    def __init__(self, base_url: str, crawl_page_list: list = None):
        """
        :params base_url: 取得したいベースのページ番号
        :params crawl_page_list: 0 ~ 34, 37までの値を含むリストで、取得したいページの番号を表している。
        """
        self.target_url_list = []
        if crawl_page_list is None:
            # default値の場合は、全ての業種の上場銘柄を取得する
            self.target_url_list = [f"base_url{i}" for i in self.numbers]
        else:
            # 特定の業種の上場銘柄を取得する場合
            self.target_url_list = [f"base_url{i}" for i in crawl_page_list]
        self.stock_info_list = []

    def crawl(self):
        """
        指定されたURLの業種の上場銘柄リストを取得する
        """
        for target_url in self.target_url_list:
            one_industry = StockBrandOneIndustryListController(
                initial_url=target_url)
            one_industry.crawl()
            self.stock_info_list.extend(one_industry.get_info())
            sleep(1)

    def get_info(self) -> list:
        return self.stock_info_list


class StockBrandOneIndustryListController:
    """
    複数ページにまたがって株の銘柄を取得するクラス
    """
    def __init__(self, initial_url: str):
        # Crawlを開始するURL
        self.initial_url = initial_url
        self.stock_info_list = []

    def crawl(self):
        stock_crawler = StockBrandListCrawler(self.initial_url)
        stock_crawler.crawl()
        self.stock_info_list.extend(stock_crawler.get_info())

        next_url = stock_crawler.get_next_url()
        # Crawlするのは最大20ページ
        for _ in range(20):
            if next_url is not None:
                stock_crawler = StockBrandListCrawler(next_url)
                stock_crawler.crawl()
                self.stock_info_list.extend(stock_crawler.get_info())
                next_url = stock_crawler.get_next_url()
                sleep(1)
            else:
                break

    def get_info(self) -> list:
        return self.stock_info_list


class StockBrandListCrawler(Crawler):
    """
    株の銘柄の一覧を取得する処理を管理する
    取得する対象は1ページのみ
    次ページへの遷移などは、上のレイヤーで管理する
    """

    def __init__(self, url: str):
        # 本ページでは1 pageのみの取得が対象になる
        self.url = url
        self.link_content = None
        self.stock_info_list = []

    def crawl(self) -> list:
        bs = self.get_beautifulsoup_result(self.url)

        # ページ中のリンク取得
        next_page_links = bs.find('div', class_="paginate_box")
        self.link_content = LinkContent(next_page_links)

        # ページ中の上場株価一覧取得
        page_content = bs.find('div', class_="md_table_wrapper")
        table_content = page_content.find_all("tr")
        for tr in table_content[1:]:
            self.stock_info_list.append(OneRow(tr))
        return self.stock_info_list

    def get_info(self) -> list:
        return self.stock_info_list

    def get_next_url(self) -> Union[str, None]:
        return self.link_content.get_next_url()
