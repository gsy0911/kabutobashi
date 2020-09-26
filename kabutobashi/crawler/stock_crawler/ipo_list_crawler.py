from kabutobashi.crawler.crawler import Crawler
from bs4 import BeautifulSoup
from typing import Union


def get_ipo_list_from_year(year: Union[str, int]) -> dict:
    """
    IPOのリストを取得する関数
    
    Args:
        year: 取得対象の年
    """
    base_url = "https://96ut.com/ipo/list.php"
    year_str = None
    if type(year) is int:
        year_str = str(year)
    else:
        year_str = year

    # TODO when 2021 has come ?
    if year_str == "2020":
        # 実行年の場合
        url = base_url
    else:
        # 過去年の場合
        url = f"{base_url}?year={year}"
    ipo_list_crawler = IPOListCrawler()
    return ipo_list_crawler(url=url)


class IPOListCrawler(Crawler):
    """
    指定した年にIPOした企業名と銘柄コードを取得する
    """

    def __init__(self):
        super().__init__()

    def web_scraping(self, text: str) -> dict:
        """
        :params text: webページ
        """
        res = BeautifulSoup(text, 'lxml')
        table_content = res.find("div", {"class": "tablewrap"})
        table_thead = table_content.find("thead")
        # headの取得
        table_head_list = []
        for th in table_thead.find_all("th"):
            table_head_list.append(th.get_text())

        # bodyの取得
        table_tbody = table_content.find("tbody")
        whole_result = {}
        for idx, tr in enumerate(table_tbody.find_all("tr")):
            table_body_dict = {}
            for header, td in zip(table_head_list, tr.find_all("td")):
                table_body_dict[header] = td.get_text().replace("\n", "")
            whole_result[idx] = table_body_dict
        return whole_result
