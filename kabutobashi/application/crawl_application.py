import pandas as pd

from kabutobashi.domain.entity.blocks.crawl_blocks import *
from kabutobashi.domain.entity.blocks.extract_blocks import *
from kabutobashi.domain.entity.blocks.pre_process_blocks import *
from kabutobashi.domain.entity.blocks.write_blocks import *
from kabutobashi.domain.services.flow import Flow


def crawl_info(code: str, database_dir: str):
    blocks = [
        CrawlStockInfoBlock,
        ExtractStockInfoBlock,
        DefaultPreProcessBlock,
        WriteStockSqlite3Block,
    ]

    res = Flow.initialize(
        params={
            "crawl_stock_info": {"code": code},
            "default_pre_process": {"for_analysis": False},
            "write_stock_sqlite3": {"database_dir": database_dir},
        }
    ).then(blocks)
    return res.block_glue["default_pre_process"].series


def crawl_info_multiple(code: str, page: str, database_dir: str) -> pd.DataFrame:
    blocks = [
        CrawlStockInfoMultipleDays2Block,
        ExtractStockInfoMultipleDays2Block,
        DefaultPreProcessBlock,
        WriteStockSqlite3Block,
    ]

    res = Flow.initialize(
        params={
            "crawl_stock_info_multiple_days_2": {"code": code, "page": page},
            "default_pre_process": {"for_analysis": False},
            "write_stock_sqlite3": {"database_dir": database_dir},
        }
    ).then(blocks)
    return res.block_glue["default_pre_process"].series


def crawl_ipo(year: str, database_dir: str):
    blocks = [
        CrawlStockIpoBlock,
        ExtractStockIpoBlock,
        WriteBrandSqlite3Block,
    ]

    res = Flow.initialize(
        params={
            "crawl_stock_ipo": {"year": year},
            "write_brand_sqlite3": {"database_dir": database_dir},
        }
    ).then(blocks)
    return res.block_glue["extract_stock_ipo"].series
