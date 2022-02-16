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
  - StockDataMultipleCode

- initial step to analyze:  ``processed``

  - StockDataProcessedBySingleMethod
  - StockDataProcessedByMultipleMethod

- second step to analyze:  ``estimated``

  - StockDataEstimatedBySingleFilter
  - StockDataEstimatedByMultipleFilter
"""
from .stock_data_estimated import StockDataEstimatedByMultipleFilter, StockDataEstimatedBySingleFilter
from .stock_data_processed import StockDataProcessedByMultipleMethod, StockDataProcessedBySingleMethod
from .stock_data_raw import StockDataMultipleCode, StockDataSingleCode, StockDataSingleDay
from .stock_ipo import StockIpo
from .weeks_52_high_low_info import Weeks52HighLow
