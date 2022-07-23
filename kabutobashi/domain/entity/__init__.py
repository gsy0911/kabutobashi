"""
define structures of the stock-data,
when processing Methods like SMA, MCAD,
and when estimating stock-code which is to rise in the next day or so on.

- Used for ``crawling``

  - StockIpo
  - Weeks52HighLow

- define data-structure: ``basement``

  - StockDataSingleDay
  - StockDataSingleCode

- initial step to analyze:  ``processed``

  - StockDataProcessedBySingleMethod
  - StockDataProcessedByMultipleMethod

- second step to analyze:  ``estimated``

  - StockDataEstimatedBySingleFilter
  - StockDataEstimatedByMultipleFilter
"""
from .stock_models import OPTIONAL_COL, REQUIRED_COL, StockBrand, StockIpo, StockRecord, Weeks52HighLow
