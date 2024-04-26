"""
Method modules provide technical analysis for stock chart.

- technical analysis

  - ADX
  - BollingerBands
  - Fitting
  - Ichimoku
  - MACD
  - Momentum
  - PsychoLogical
  - SMA
  - Stochastics

- other

  - Basic: only used `parameterize`

"""

from .adx import AdxProcess, adx
from .basic import BasicProcess, basic
from .bollinger_bands import BollingerBandsProcess, bollinger_bands
from .fitting import FittingProcess, fitting
from .ichimoku import IchimokuProcess, ichimoku
from .industry_cat import IndustryCategoriesProcess, industry_categories
from .macd import MacdProcess, macd
from .method import Method, ProcessMethod
from .momentum import MomentumProcess, momentum
from .pct_change import PctChangeProcess, pct_change
from .psycho_logical import PsychoLogicalProcess, psycho_logical
from .sma import SmaProcess, sma
from .stochastics import StochasticsProcess, stochastics
from .volatility import VolatilityProcess, volatility
