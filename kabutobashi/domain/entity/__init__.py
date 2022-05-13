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
from .stock_data_estimated import StockDataEstimatedBySingleFilter
from .stock_data_processed import StockDataProcessedBySingleMethod
from .stock_data_raw import IStockRecordsetRepository, StockBrand, StockDataSingleCode, StockRecord, StockRecordset
from .stock_data_visualized import StockDataVisualized
from .stock_ipo import StockIpo
from .weeks_52_high_low_info import Weeks52HighLow
