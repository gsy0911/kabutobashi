from concurrent.futures import ThreadPoolExecutor
from typing import List, Union
from logging import getLogger

from kabutobashi.domain.errors import KabutobashiPageError
from kabutobashi.domain.entity import StockPageHtml
from kabutobashi.domain.services import StockInfoHtmlDecoder

from .stock_ipo_page import StockIpoPage
from .weeks_52_high_low_page import Weeks52HighLowPage


logger = getLogger(__name__)


def crawl_single(code: Union[int, str], dt: str) -> dict:
    try:
        stock_page_html = StockPageHtml.from_url(
            url=f"https://minkabu.jp/stock/{code}",
            code=code,
            dt=dt,
            page_type="info"
        )
        result = StockInfoHtmlDecoder(page_html=stock_page_html).decode()
        return result
    except KabutobashiPageError:
        return {}
    except AttributeError:
        logger.exception(f"error occurred at: {code}")
        return {}
    except Exception:
        logger.exception(f"error occurred at: {code}")
        return {}


def crawl_multiple(code_list: List[Union[int, str]], dt: str, max_workers: int = 2) -> List[dict]:
    response_list = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        map_gen = executor.map(crawl_single, code_list, dt)
        for response in map_gen:
            response_list.append(response)
    return response_list
