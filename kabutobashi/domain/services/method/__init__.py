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
from .adx import ADX, AdxProcess
from .basic import Basic, BasicProcess
from .bollinger_bands import BollingerBands, BollingerBandsProcess
from .fitting import Fitting, FittingProcess
from .ichimoku import Ichimoku, IchimokuProcess
from .industry_cat import IndustryCategories, IndustryCategoriesProcess
from .macd import MACD, MacdProcess
from .method import Method, ProcessMethod
from .momentum import Momentum, MomentumProcess
from .pct_change import PctChange, PctChangeProcess
from .psycho_logical import PsychoLogical, PsychoLogicalProcess
from .sma import SMA, SmaProcess
from .stochastics import Stochastics, StochasticsProcess
from .volatility import Volatility, VolatilityProcess
