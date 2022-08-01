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
from .adx import adx
from .basic import basic
from .bollinger_bands import bollinger_bands
from .fitting import fitting
from .ichimoku import ichimoku
from .industry_cat import industry_categories
from .macd import macd
from .method import Method, ProcessMethod
from .momentum import momentum
from .pct_change import pct_change
from .psycho_logical import psycho_logical
from .sma import sma
from .stochastics import stochastics
from .volatility import volatility
