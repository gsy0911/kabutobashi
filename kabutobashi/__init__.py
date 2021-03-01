# methods to analysis
from kabutobashi.method import (
    Method,
    SMA,
    MACD,
    Stochastics,
    ADX,
    BollingerBands,
    Ichimoku,
    Momentum,
    PsychoLogical,
    Fitting
)

from kabutobashi.core import (
    # technical analysis function
    analysis_with,
    # get buy or sell signal value
    get_impact_with
)

# functions to load or save files
from kabutobashi.io import (
    # read csv data
    read_csv,
    # provide example stock data
    example_data,
    # read stock data
    read_stock_csv
)

# import errors
from kabutobashi import errors

# classes or functions about crawl web pages
from kabutobashi.crawler import (
    # beautifulsoupを利用してウェブページを取得する
    get_web_page,
    # 単一の株価の詳細情報を取得する
    get_stock_detail,
    # ある年にIPOした銘柄の情報を取得する
    get_ipo_list_from_year,
    # 52週高値・底値を取得する関数
    get_52_weeks_high_low
)

from .utilities import (
    # n営業日前までの日付のリストを返す関数
    get_past_n_days,
    # 銘柄コードでイテレーションする関数
    iter_by_code,
    # window幅でデータを取得しつつデータを返す関数
    train_test_sliding_split,
    # 株価の動きを様々な統計量で表現
    compute_statistical_values

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
fitting = Fitting()

# comparable tuple
VERSION = (0, 1, 6)
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
