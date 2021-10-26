import pytest

import kabutobashi as kb


class TestStockInfo:
    def test_error_init(self):
        with pytest.raises(kb.errors.KabutobashiEntityError):
            _ = kb.StockInfo(
                code="1234",
                market="market",
                name="",
                industry_type="industry_type",
                open="",
                high="",
                low="",
                close="",
                psr="",
                per="",
                pbr="",
                volume="",
                unit="",
                market_capitalization="",
                issued_shares="",
                dt="",
            )


class TestStockIpo:
    def test_error_init(self):
        with pytest.raises(kb.errors.KabutobashiEntityError):
            _ = kb.StockIpo(
                code="", market="", manager="", stock_listing_at="", public_offering="", evaluation="", initial_price=""
            )


class TestWeeks52HihLow:
    def test_error_init(self):
        with pytest.raises(kb.errors.KabutobashiEntityError):
            _ = kb.Weeks52HighLow(
                code="", brand_name="", close="", buy_or_sell="", volatility_ratio="", volatility_value=""
            )
