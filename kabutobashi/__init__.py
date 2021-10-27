# methods to analysis
# import errors
from kabutobashi import errors
from kabutobashi.core import (  # technical analysis function; get buy or sell signal value
    analysis_with, get_impact_with)
from kabutobashi.domain.method import (ADX, MACD, SMA, BollingerBands, Fitting,
                                       Ichimoku, Method, Momentum,
                                       PsychoLogical, Stochastics)
# functions to load or save files
from kabutobashi.io import (  # read csv data; provide example stock data; read stock data
    example_data, read_csv, read_stock_csv)

from .domain.entity import StockInfo, StockIpo, Weeks52HighLow
# classes or functions about crawl web pages
from .domain.page import (  # ある年にIPOした銘柄の情報を取得する; 単一の株価の詳細情報を取得する; 52週高値底値の値を取得
    StockInfoPage, StockIpoPage, Weeks52HighLowPage)
from .utilities import (  # n営業日前までの日付のリストを返す関数; 銘柄コードでイテレーションする関数; window幅でデータを取得しつつデータを返す関数; 株価の動きを様々な統計量で表現
    compute_statistical_values, get_past_n_days, iter_by_code,
    train_test_sliding_split)

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
VERSION = (0, 2, 2)
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
