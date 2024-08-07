import pandas as pd

from kabutobashi.domain.entity.blocks.crawl_blocks import *
from kabutobashi.domain.entity.blocks.extract_blocks import *
from kabutobashi.domain.entity.blocks.pre_process_blocks import *
from kabutobashi.domain.entity.blocks.read_blocks import ReadSqlite3Block
from kabutobashi.domain.entity.blocks.write_blocks import *
from kabutobashi.domain.errors import KabutobashiBlockSeriesDtIsMissingError
from kabutobashi.domain.services.flow import Flow
from kabutobashi.infrastructure.repository import KabutobashiDatabase


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


def crawl_missing_info(code: str, database_dir: str):
    detect_blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
    ]

    try:
        Flow.initialize(
            params={
                "read_sqlite3": {"code": code, "database_dir": database_dir},
                "write_impact_sqlite3": {"database_dir": database_dir},
            }
        ).then(detect_blocks)
    except KabutobashiBlockSeriesDtIsMissingError as e:

        blocks = [
            CrawlStockInfoMultipleDays2Block,
            ExtractStockInfoMultipleDays2Block,
            DefaultPreProcessBlock,
        ]

        res = Flow.initialize(
            params={
                "crawl_stock_info_multiple_days_2": {"code": code, "page": "1"},
                "default_pre_process": {"for_analysis": False},
            }
        ).then(blocks)
        df = res.block_glue["default_pre_process"].series
        df = df.reset_index(drop=True)
        missing_dt = pd.DataFrame(e.dt, columns=["dt"])
        merged = pd.merge(df, missing_dt, on="dt", how="inner")

        db = KabutobashiDatabase(database_dir=database_dir)
        db.insert_stock_df(df=merged)
        return {"status": "success", "rows": len(merged.index)}
    return {"status": "success", "rows": 0}
