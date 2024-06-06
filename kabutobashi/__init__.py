from .application import crawl_info, crawl_info_multiple, crawl_ipo, decode_brand_list
from .domain import errors
from .domain.entity import Stock
from .domain.entity.blocks import block
from .domain.services.flow import Flow

# methods to analysis
from .domain.services.method import (
    Method,
    basic,
    fitting,
    ichimoku,
    industry_categories,
    pct_change,
    volatility,
)
from .domain.values import (
    DecodeHtmlPageStockIpo,
    RawHtmlPageStockInfo,
    RawHtmlPageStockInfoMultipleDaysMain,
    RawHtmlPageStockInfoMultipleDaysSub,
    RawHtmlPageStockIpo,
    StockDataEstimated,
    StockDataProcessed,
    StockDataVisualized,
)
from .example_data import example

# n営業日前までの日付のリストを返す関数
from .utilities import get_past_n_days

methods = [fitting, basic]

# comparable tuple
VERSION = (0, 8, 0)
# generate __version__ via VERSION tuple
__version__ = ".".join(map(str, VERSION))

# module level doc-string
__doc__ = """
kabutobashi
===========

**kabutobashi** is a Python package to analysis stock data with measure
analysis methods, such as MACD, SMA, etc.

Main Features
-------------
Here are the things that kabutobashi does well:
 - Easy crawl.
 - Easy analysis.
"""
