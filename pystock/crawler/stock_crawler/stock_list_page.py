from pystock.crawler.page import Page
from pystock.attributes.attribute import PageContent
from typing import Union
from bs4 import BeautifulSoup
import pandas as pd


class LinkContent(Page):
    """
    リンク先を取得する
    """

    # link_parent
    url_format = "https://minkabu.jp{}"

    def __init__(self, next_page_link: BeautifulSoup):
        super().__init__()
        # 行先: link からなるdict

        self.link_dict = {}
        if next_page_link is None:
            # データが存在しない場合もあるため
            return
        for anchor in next_page_link.find_all("a"):
            next_string = anchor.string
            if len(next_string) > 2:
                next_string = "next"
            self.link_dict[next_string] = self.url_format.format(anchor.get("href"))

    def get_info(self) -> dict:
        return self.link_dict

    def get_next_url(self) -> Union[str, None]:
        if "next" in self.link_dict:
            return self.link_dict['next']
        else:
            return None


class OneRow(Page):
    code = PageContent(tag1="div", _class1="md_sub")
    name = PageContent(tag1="div", _class1="fwb ellipsis", tag2="a")
    stock_price = PageContent(tag1="div", _class1="ly_col ly_colsize_7 wsnw")
    date = PageContent(tag1="div", _class1="ly_col ly_colsize_5 fcgl wsnw")
    objective_stock_price = PageContent(tag1="div", _class1="ly_col ly_colsize_7_fix tar", tag2="span")

    def __init__(self, tr: BeautifulSoup):
        self.code = tr
        self.name = tr
        self.stock_price = tr
        self.objective_stock_price = tr

    def get_info(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "stock_price": self.stock_price,
            "date": self.date,
            "objective_stock_price": self.objective_stock_price
        }

    @staticmethod
    def convert_to_df(one_row_list: list) -> pd.DataFrame:
        result_dict = {}
        for r in one_row_list:
            info = r.get_info()
            if info['code'] != "上場廃止":
                result_dict[info['code']] = info
        df = pd.DataFrame.from_dict(result_dict, orient="index")
        return df
