from pystock.crawler.crawler import Crawler
from pystock.crawler.stock_crawler.ipo_list_page import IPOListPage


class IPOListCrawler(Crawler):
    """
    指定した年にIPOした企業名と銘柄コードを取得する
    """

    def __init__(self, url: str):
        self.url = url

    def crawl(self) -> dict:
        """
        urlをcrawlし、取得した結果を返す関数
        """
        bs = self.get_beautifulsoup_result(self.url)
        mb = bs.find("div", class_="Mainbox")

        months = mb.find_all('div', class_="fClear mb60")

        # crawl
        whole_dict = {}
        for m in months:
            ipo = IPOListPage(m)
            whole_dict[ipo.month_text] = ipo.get_info()
        return whole_dict

#     12月
# =======================
# スポーツフィールド
# (7080)

# -----------------------
# 総合評価 : 
# 上場市場 : 東証マザーズ
# 申込期間 : 12/11～12/17
# 上場日 : 12/26
# 当たり本数 : 3,470本
# 想定価格 : 2,650円
# 仮条件 : 2,570円～2,730円
# 公募価格 : 2,730円
# 初値 : 8,500円
# 初値上昇率 : +5,770円（+211.4％）
# 狙い目証券 : 
# SMBC日興（主）
# SBI（副）
# 岩井
# マネックス
# 松井
# DMM株
# ライブスター

# =======================
# WDBココ
# (7079)

# -----------------------
# 総合評価 : 
# 上場市場 : 東証マザーズ
# 申込期間 : 12/9～12/13
# 上場日 : 12/25
# 当たり本数 : 6,578本
# 想定価格 : 1,390円
# 仮条件 : 1,390円～1,530円
# 公募価格 : 1,530円
# 初値 : 3,400円
# 初値上昇率 : +1,870円（+122.2％）
# 狙い目証券 : 
# SMBC日興（主）
# SBI
# 楽天
# DMM株
