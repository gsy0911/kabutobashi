from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union

from kabutobashi.domain.entity.stock import Stock, StockBrand, StockPriceRecord, StockReferenceIndicator
from kabutobashi.domain.values import DecodedHtmlPage, StockInfoMinkabuTopPage, StockIpo
from kabutobashi.utilities import convert_float, convert_int


class IEntityConverter(ABC):
    pass


class StockConverter(IEntityConverter):
    def convert(self, value_object: Union[StockIpo, StockInfoMinkabuTopPage]) -> Stock:
        if type(value_object) is StockInfoMinkabuTopPage:
            return self._convert_stock_info_minkabu_top_page(value_object=value_object)

    @staticmethod
    def _convert_stock_info_minkabu_top_page(value_object: StockInfoMinkabuTopPage) -> Stock:
        data = value_object.to_dict()
        stock_brand = StockBrand.from_dict(data)
        stock_reference_indicator = StockReferenceIndicator.from_dict(data)

        return Stock(
            code=value_object.code,
            brand=stock_brand,
            daily_price_records=[StockPriceRecord.from_dict(data)],
            reference_indicator=stock_reference_indicator,
        )
