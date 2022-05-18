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
from .adx import ADX
from .basic import Basic
from .bollinger_bands import BollingerBands
from .fitting import Fitting
from .ichimoku import Ichimoku
from .industry_cat import IndustryCategories
from .macd import MACD
from .method import Method
from .momentum import Momentum
from .pct_change import PctChange
from .psycho_logical import PsychoLogical
from .sma import SMA
from .stochastics import Stochastics
from .volatility import Volatility
