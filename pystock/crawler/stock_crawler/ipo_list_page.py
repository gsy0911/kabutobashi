from pystock.crawler.page import Page
from pystock.attributes.attribute import PageContent
from bs4 import BeautifulSoup


class IPOListPage(Page):
    """
    一ヶ月間のIPOの情報を取得するクラス
    """
    table_body_header = {
        "総合評価": "ipo_score",
        "上場市場": "ipo_market",
        "申込期間": "application_priod",
        "上場日": "ipo_date",
        "当たり本数": "successful_candidate",
        "想定価格": "assumption_price",
        "仮条件": "condition_price",
        "公募価格": "open_price",
        "初値": "initial_open_price",
        "初値上昇率": "initial_close_price",
        "狙い目証券": "stock_company"
    }

    def __init__(self, one_month: BeautifulSoup):
        self.month_text = one_month.find("h2").get_text()

        # 企業名と銘柄コードを含む列
        table_head = one_month.find("div", class_="tableHead")
        head_tr_s = table_head.find_all("tr")

        # IPOに関する情報がある列
        table_body = one_month.find("div", class_="tableBody")
        body_tr_s = table_body.find_all("tr")

        # 月次のIPOのリストを取得
        self.one_month_ipo_dict = {}
        for head, body in zip(head_tr_s, body_tr_s):
            one_ipo_dict = {}
            for bh, b in zip(list(self.table_body_header.values()), body.find_all("td")):
                one_ipo_dict[bh] = b.get_text()
        self.one_month_ipo_dict[head.get_text()] = one_ipo_dict

    def get_info(self) -> dict:
        return self.one_month_ipo_dict
