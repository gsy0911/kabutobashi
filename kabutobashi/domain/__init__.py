"""
define structures of the stock-data,
when processing Methods like SMA, MCAD,
and when estimating stock-code which is to rise in the next day or so on.

- Used for ``crawling``

  - value_object.StockIpo

- define data-structure: ``basement``

  - entity.Stock
  - aggregates.StockCodeSingleAggregate

- initial step to analyze:  ``processed``

  - value_object.StockDataProcessed

- second step to analyze:  ``estimated``

  - value_object.StockDataEstimated
"""
