import pandas as pd

from kabutobashi.domain.entity.blocks.parameterize_blocks import *
from kabutobashi.domain.entity.blocks.pre_process_blocks import *
from kabutobashi.domain.entity.blocks.process_blocks import *
from kabutobashi.domain.entity.blocks.read_blocks import *
from kabutobashi.domain.entity.blocks.reduce_blocks import *
from kabutobashi.domain.services.flow import Flow, FlowPath

PARAMS = {"read_sqlite3": {"code": 1439}, "default_pre_process": {"for_analysis": True}}
PARAMS_LIST = (
    FlowPath()
    .read_example(code=1439)
    .apply_default_pre_process()
    .sma()
    .macd()
    .adx()
    .bollinger_bands()
    .momentum()
    .psycho_logical()
    .stochastics()
    .volatility()
    .pct_change()
    .dumps()
)


def test_block_impact():
    blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
        ProcessSmaBlock,
        ParameterizeSmaBlock,
        ProcessMacdBlock,
        ParameterizeMacdBlock,
        ProcessAdxBlock,
        ParameterizeAdxBlock,
        ProcessBollingerBandsBlock,
        ParameterizeBollingerBandsBlock,
        ProcessMomentumBlock,
        ParameterizeMomentumBlock,
        ProcessPsychoLogicalBlock,
        ParameterizePsychoLogicalBlock,
        ProcessStochasticsBlock,
        ParameterizeStochasticsBlock,
        ParameterizeVolatilityBlock,
        ParameterizePctChangeBlock,
        FullyConnectBlock,
    ]
    res = Flow.initialize(params=PARAMS).then(blocks)
    params = res.block_glue["fully_connect"].params
    assert params["impact"] == 0.151225

    series = res.block_glue["fully_connect"].series
    assert_df = pd.DataFrame.from_dict({"code": [1439], "dt": ["2021-11-26"], "impact": [0.151225]})
    assert series.equals(assert_df)
