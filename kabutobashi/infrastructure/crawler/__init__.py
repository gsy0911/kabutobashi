import functools
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
from typing import List, Union

from kabutobashi.domain.errors import KabutobashiPageError
from kabutobashi.domain.services import StockInfoHtmlDecoder
from kabutobashi.domain.values import StockPageHtml

from .stock_ipo_page import StockIpoPage
from .weeks_52_high_low_page import Weeks52HighLowPage

logger = getLogger(__name__)


def crawl_single(code: Union[int, str], dt: str) -> dict:
    try:
        stock_page_html = StockPageHtml.from_url(
            url=f"https://minkabu.jp/stock/{code}", code=code, dt=dt, page_type="info"
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
    partial_crawl_single = functools.partial(crawl_single, dt=dt)
    response_list = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        map_gen = executor.map(partial_crawl_single, code_list)
        for response in map_gen:
            response_list.append(response)
    return response_list
