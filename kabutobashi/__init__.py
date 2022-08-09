# import seaborn as sns

# import errors
from kabutobashi.domain.services import SaFundamental, SaVolume, StockAnalysis

# methods to analysis
from kabutobashi.domain.services.method import (
    Method,
    adx,
    basic,
    bollinger_bands,
    fitting,
    ichimoku,
    industry_categories,
    macd,
    momentum,
    pct_change,
    psycho_logical,
    sma,
    stochastics,
    volatility,
)

from .domain import errors
from .domain.aggregates import StockCodeSingleAggregate
from .domain.entity import OPTIONAL_COL, REQUIRED_COL, StockBrand, StockIpo, StockRecord, Weeks52HighLow
from .domain.services import StockInfoMultipleDaysHtmlDecoder, StockIpoHtmlDecoder, Weeks52HighLowHtmlDecoder
from .domain.values import (
    StockDataEstimated,
    StockDataVisualized,
    StockInfoHtmlPage,
    StockInfoMultipleDaysMainHtmlPage,
    StockInfoMultipleDaysSubHtmlPage,
    StockIpoHtmlPage,
    StockRecordset,
    StockWeeks52HighLowHtmlPage,
)
from .example_data import example
from .infrastructure.repository import StockRecordsetCrawler, StockRecordsetStorageBasicRepository

# n営業日前までの日付のリストを返す関数; 銘柄コードでイテレーションする関数; window幅でデータを取得しつつデータを返す関数; 株価の動きを様々な統計量で表現
from .utilities import get_past_n_days

# sns.set()

methods = [sma, macd, stochastics, adx, bollinger_bands, momentum, psycho_logical, fitting, basic]

# estimate filters
sa_fundamental = SaFundamental()
sa_volume = SaVolume()

stock_analysis = [sa_fundamental, sa_volume]

# comparable tuple
VERSION = (0, 4, 5)
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
