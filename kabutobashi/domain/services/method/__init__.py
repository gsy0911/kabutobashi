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

from .basic import BasicProcess, basic
from .fitting import FittingProcess, fitting
from .ichimoku import IchimokuProcess, ichimoku
from .industry_cat import IndustryCategoriesProcess, industry_categories
from .method import Method, ProcessMethod
from .pct_change import PctChangeProcess, pct_change
from .volatility import VolatilityProcess, volatility
