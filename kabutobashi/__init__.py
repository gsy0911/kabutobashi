from .application import analysis, crawl_info, crawl_info_multiple, crawl_ipo, crawl_missing_info, decode_brand_list
from .domain import errors
from .domain.entity.blocks import block
from .domain.services.flow import Flow, FlowPath

# methods to analysis
from .domain.values import DecodeHtmlPageStockIpo, RawHtmlPageStockInfo, RawHtmlPageStockIpo
from .example_data import example
from .infrastructure.repository import KabutobashiDatabase

# n営業日前までの日付のリストを返す関数
from .utilities import get_past_n_days

# comparable tuple
VERSION = (0, 8, 7)
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
