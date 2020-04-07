# methods to analysis
from pystock.method.api import (
    Method,
    SMA,
    MACD,
    Stochastics,
    ADX,
    BollingerBands,
    Ichimoku,
    Momentum,
    PsychoLogical
)

from pystock.core import (
    # technical analysis function
    analysis_with,
    # get buy or sell signal value
    get_impact_with
)

# functions to load or save files
from pystock.io.api import (
    # read csv data
    read_csv,
    # provide example stock data
    example_data,
    # read stock data
    read_stock_csv
)

# import errors
from pystock import errors

# classes or functions about crawl web pages
from pystock.crawler.api import (
    # beautifulsoupを利用してウェブページを取得する
    get_webpage,
    # 単一の株価の詳細情報を取得する
    get_stock_detail,
    # ある年にIPOした銘柄の情報を取得する
    get_ipo_list_from_year,
    # 52週高値・底値を取得する関数
    get_52_weeks_high_low
)

# create and initialize instance
sma = SMA(short_term=5, medium_term=21, long_term=70)
macd = MACD(short_term=12, long_term=26, macd_span=9)
stochastics = Stochastics()
adx = ADX()
bollinger_bands = BollingerBands()
ichimoku = Ichimoku()
momentum = Momentum()
psycho_logical = PsychoLogical()

__version__ = "0.1.0"

# module level doc-string
__doc__ = """
pystock
=======

**pystock** is a Python package to analysis stock data with measure
analysis methods, such as MACD, SMA, etc.

Main Features
-------------
Here are the things that pystock does well:
 - Easy crawl.
 - Easy analysis.
"""
