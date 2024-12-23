"""
kabutobashi
===========

A Python package for stock market analysis and data crawling.

This package provides tools for:
- Stock data crawling and parsing
- Technical analysis (MACD, SMA, etc.)
- Market data management and storage
- Historical data analysis

Main Features
-------------
- Efficient data crawling from multiple sources
- Comprehensive technical analysis tools
- Easy-to-use API for market data analysis
- Robust error handling and data validation
"""

# Version information
VERSION = (0, 8, 7)
__version__ = ".".join(map(str, VERSION))

# Application layer imports
from .application import (
    analysis,
    crawl_info,
    crawl_info_multiple,
    crawl_ipo,
    crawl_missing_info,
    decode_brand_list,
)

# Domain layer imports
from .domain import errors
from .domain.entity.blocks import block
from .domain.services.flow import Flow, FlowPath
from .domain.values import (
    DecodeHtmlPageStockIpo,
    RawHtmlPageStockInfo,
    RawHtmlPageStockIpo,
)

# Infrastructure layer imports
from .infrastructure.repository import KabutobashiDatabase

# Utility functions
from .utilities import get_past_n_days

# Example data
from .example_data import example

# Define public API
__all__ = [
    'analysis',
    'crawl_info',
    'crawl_info_multiple',
    'crawl_ipo',
    'crawl_missing_info',
    'decode_brand_list',
    'errors',
    'block',
    'Flow',
    'FlowPath',
    'DecodeHtmlPageStockIpo',
    'RawHtmlPageStockInfo',
    'RawHtmlPageStockIpo',
    'KabutobashiDatabase',
    'get_past_n_days',
    'example',
]
