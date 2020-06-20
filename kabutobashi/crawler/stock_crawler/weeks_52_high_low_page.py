from kabutobashi.crawler.page import Page
from kabutobashi.attributes import PageContent
from bs4 import BeautifulSoup


class Week52HighLowStockPricePageTable(Page):
    """
    を取得する
    """
    def __init__(self, content: BeautifulSoup):
        # テーブル要素をすべて取得
        table = content.find_all("tr")
        self.result_list = list()
        for t in table:
            row = Week52HighLowStockPricePageRow(t)
            self.result_list.append(row.get_info())

    def get_info(self) -> dict:
        return {"data": self.result_list}


class Week52HighLowStockPricePageRow(Page):
    # ここからcrawlするページのタグ
    cell = "tv-screener-table__cell"
    signal = "tv-screener-table__signal"
    close_tag = f"tv-data-table__cell {cell} {cell}--big"
    # タグ
    volatility_up_tag = f"{close_tag} {cell}--up"
    volatility_down_tag = f"{close_tag} {cell}--down"
    buy_tag = f"{signal} {signal}--buy"
    strong_buy_tag = f"{signal} {signal}--strong-buy"
    sell_tag = f"{signal} {signal}--sell"
    strong_sell_tag = f"{signal} {signal}--strong-sell"
    # 取得する内容
    code = PageContent(tag1="a", required=True)
    brand_name = PageContent(tag1="span", required=True)
    close = PageContent(tag1="td", _class1=close_tag, required=True)
    volatility_up = PageContent(tag1="td", _class1=volatility_up_tag)
    volatility_down = PageContent(tag1="td", _class1=volatility_down_tag)
    buy = PageContent(tag1="span", _class1=buy_tag, alternative_data="")
    strong_buy = PageContent(tag1="span", _class1=strong_buy_tag, alternative_data="")
    sell = PageContent(tag1="span", _class1=sell_tag, alternative_data="")
    strong_sell = PageContent(tag1="span", _class1=strong_sell_tag, alternative_data="")

    def __init__(self, row: BeautifulSoup):
        self.code = row
        self.brand_name = row
        self.close = row
        self.buy = row
        self.strong_buy = row
        self.sell = row
        self.strong_sell = row
        self.buy_or_sell = f"{self.buy}{self.strong_buy}{self.sell}{self.strong_sell}"
        volatility_dict = self._crawl_volatility_info(row)
        self.volatility_ratio = volatility_dict.get("volatility_ratio", "-")
        self.volatility_value = volatility_dict.get("volatility_value", "-")

    def get_info(self) -> dict:
        return {
            "code": self.code,
            "brand_name": self.brand_name,
            "close": self.close,
            "buy_or_sell": self.buy_or_sell,
            "volatility_ratio": self.volatility_ratio,
            "volatility_value": self.volatility_value
        }

    def _crawl_volatility_info(self, table: BeautifulSoup) -> dict:
        # 上がったか、下がったかを判断するリスト
        evaluate_list = list()
        evaluate_list.extend(table.find_all("td", class_=self.volatility_up_tag))
        evaluate_list.extend(table.find_all("td", class_=self.volatility_down_tag))
        return self._volatility_replace_method(volatility_list=evaluate_list)

    @staticmethod
    def _volatility_replace_method(volatility_list: list) -> dict:
        """
        volatility_listにはweb pageから取得したデータが入っている
        suffixには高値か底値かを表す接頭辞を表す
        """
        if len(volatility_list) == 0:
            return {}
        rate_candidate = volatility_list[0].text
        value_candidate = volatility_list[1].text
        return {
            "volatility_ratio": rate_candidate,
            "volatility_value": value_candidate
            }
