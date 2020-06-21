from kabutobashi.crawler.crawler import Crawler

# 単一銘柄の詳細情報を取得するクラス
from kabutobashi.crawler.stock_crawler.stock_detail_crawler import (
    get_stock_detail
)

from kabutobashi.crawler.stock_crawler.ipo_list_crawler import (
    get_ipo_list_from_year
)

from kabutobashi.crawler.stock_crawler.weeks_52_high_low_crawler import (
    get_52_weeks_high_low
)


def get_web_page(url: str) -> str:
    return Crawler().get_url_text(url)
