from bs4 import BeautifulSoup
from kabutobashi.crawler.page import Page
from kabutobashi.attributes import PageContent


class StockBoard(Page):
    """
    ページ上部の以下の項目を取得する
    
    * stock_label: {code} {市場}
    * name: {銘柄名}
    * date: 株価MM/DD
    * close: 終値
    
    """
    stock_label = PageContent(tag1="div", _class1="stock_label")
    name = PageContent(tag1="p", _class1="md_stockBoard_stockName")
    date = PageContent(tag1="h2", _class1="stock_label fsl")
    close = PageContent(tag1="div", _class1="stock_price")

    def __init__(self, stock_board: BeautifulSoup):
        super().__init__()
        self.stock_label = stock_board
        self.name = stock_board
        self.date = stock_board
        self.close = stock_board

    def get_info(self) -> dict:
        return {
            "stock_label": self.stock_label,
            "name": self.name,
            "close": self.close,
            "date": self.date,
        }


class StockDetail(Page):
    """
    ページ中央の情報を取得する
    """

    industry_type = PageContent(
        tag1="div",
        _class1="ly_content_wrapper size_ss")

    def __init__(self, stock_detail: BeautifulSoup):
        self.industry_type = stock_detail

        info = {}
        for li in stock_detail.find_all("li", {"class": "ly_vamd"}):
            info[li.find("dt").get_text()] = li.find("dd").get_text()
        self.open = info['始値']
        self.high = info['高値']
        self.low = info['安値']
        self.unit = info['単元株数']
        self.per = info['PER(調整後)']
        self.psr = info['PSR']
        self.pbr = info['PBR']
        self.volume = info['出来高']
        self.market_capitalization = info['時価総額']
        self.issued_shares = info['発行済株数']

    def get_info(self) -> dict:
        return {
            "industry_type": self.industry_type,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "unit": self.unit,
            "per": self.per,
            "psr": self.psr,
            "pbr": self.pbr,
            "volume": self.volume,
            "market_capitalization": self.market_capitalization,
            "issued_shares": self.issued_shares
        }
