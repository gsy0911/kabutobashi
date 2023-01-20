from typing import List, Union

from kabutobashi.domain.entity.stock import Stock, StockBrand, StockPriceRecord, StockReferenceIndicator
from kabutobashi.domain.values import (
    DecodeHtmlPageStockInfoMinkabuTop,
    DecodeHtmlPageStockInfoMultipleDays,
    DecodeHtmlPageStockIpo,
)


class StockConverter:
    def convert(
        self,
        value_object: Union[
            DecodeHtmlPageStockIpo, DecodeHtmlPageStockInfoMinkabuTop, List[DecodeHtmlPageStockInfoMultipleDays]
        ],
    ) -> Stock:
        if type(value_object) is DecodeHtmlPageStockInfoMinkabuTop:
            return self._convert_stock_info_minkabu_top_page(value_object=value_object)
        elif type(value_object) is DecodeHtmlPageStockIpo:
            return self._convert_stock_ipo_page(value_object=value_object)
        elif type(value_object) is list:
            if all([type(v) is DecodeHtmlPageStockInfoMultipleDays for v in value_object]):
                return self._convert_stock_info_multiple_days_list(value_object=value_object)
        else:
            raise ValueError()

    @staticmethod
    def _convert_stock_info_minkabu_top_page(value_object: DecodeHtmlPageStockInfoMinkabuTop) -> Stock:
        data = value_object.to_dict()

        stock_brand = StockBrand.from_dict(data)
        stock_reference_indicator = StockReferenceIndicator.from_dict(data)

        return Stock(
            code=value_object.code,
            brand=stock_brand,
            daily_price_records=[StockPriceRecord.from_dict(data)],
            reference_indicator=stock_reference_indicator,
        )

    @staticmethod
    def _convert_stock_info_multiple_days(value_object: DecodeHtmlPageStockInfoMultipleDays) -> Stock:
        data = value_object.to_dict()

        stock_brand = StockBrand.from_dict(data)
        stock_reference_indicator = StockReferenceIndicator.from_dict(data)
        return Stock(
            code=value_object.code,
            brand=stock_brand,
            daily_price_records=[StockPriceRecord.from_dict(data)],
            reference_indicator=stock_reference_indicator,
        )

    @staticmethod
    def _convert_stock_info_multiple_days_list(value_object: List[DecodeHtmlPageStockInfoMultipleDays]) -> Stock:
        return Stock.reduce(stocks=[StockConverter._convert_stock_info_multiple_days(v) for v in value_object])

    @staticmethod
    def _convert_stock_ipo_page(value_object: DecodeHtmlPageStockIpo) -> Stock:

        data = value_object.to_dict()
        stock_brand = StockBrand.from_dict(data)

        return Stock(
            code=value_object.code,
            brand=stock_brand,
            daily_price_records=[],
            reference_indicator=None,
        )
