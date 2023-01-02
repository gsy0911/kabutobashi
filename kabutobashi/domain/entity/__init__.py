"""
define structures of the stock-data,
when processing Methods like SMA, MCAD,
and when estimating stock-code which is to rise in the next day or so on.

- Used for ``crawling``

  - StockIpo
  - Weeks52HighLow

- define data-structure: ``basement``

  - StockRecordset
  - StockCodeSingleAggregate

- initial step to analyze:  ``processed``

  - StockDataProcessed

- second step to analyze:  ``estimated``

  - StockDataEstimated
"""
from .stock import Stock
