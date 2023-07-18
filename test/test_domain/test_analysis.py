# pro = stock_agg.with_estimated(ANALYSIS)

import pytest

import kabutobashi as kb


@pytest.fixture(scope="module", autouse=True)
def stock_agg() -> kb.StockCodeSingleAggregate:
    df = kb.example()
    yield kb.StockCodeSingleAggregate.of(entity=df, code="1375")


def test_analysis_with_fundamental(stock_agg):
    with pytest.raises(KeyError):
        _ = stock_agg.with_processed([]).with_estimated(kb.stock_analysis)
    with pytest.raises(KeyError):
        _ = stock_agg.with_processed([kb.sma]).with_estimated(kb.stock_analysis)
    with pytest.raises(KeyError):
        _ = stock_agg.with_processed([kb.sma, kb.macd]).with_estimated(kb.stock_analysis)
    with pytest.raises(KeyError):
        _ = stock_agg.with_processed([kb.sma, kb.macd, kb.stochastics]).with_estimated(kb.stock_analysis)
    with pytest.raises(KeyError):
        _ = stock_agg.with_processed([kb.sma, kb.macd, kb.stochastics, kb.bollinger_bands]).with_estimated(
            kb.stock_analysis
        )
    with pytest.raises(KeyError):
        _ = stock_agg.with_processed([kb.sma, kb.macd, kb.stochastics, kb.bollinger_bands, kb.momentum]).with_estimated(
            kb.stock_analysis
        )
    with pytest.raises(KeyError):
        _ = stock_agg.with_processed(
            [kb.sma, kb.macd, kb.stochastics, kb.bollinger_bands, kb.momentum, kb.psycho_logical]
        ).with_estimated(kb.stock_analysis)
