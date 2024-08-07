from test.conftest import DATABASE_DIR

from kabutobashi.domain.entity.blocks.parameterize_blocks import *
from kabutobashi.domain.entity.blocks.pre_process_blocks import *
from kabutobashi.domain.entity.blocks.process_blocks import *
from kabutobashi.domain.entity.blocks.read_blocks import *
from kabutobashi.domain.services.flow import Flow, FlowPath

PARAMS = {"read_example": {"code": 1439, "database_dir": DATABASE_DIR}, "default_pre_process": {"for_analysis": True}}
PARAMS2 = {"read_sqlite3": {"code": 1439, "database_dir": DATABASE_DIR}, "default_pre_process": {"for_analysis": True}}
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
PARAMS_LIST2 = (
    FlowPath()
    .read_sqlite3(code=1439, database_dir=DATABASE_DIR)
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


def test_block_parameterize_sma():
    blocks = [
        ReadExampleBlock,
        DefaultPreProcessBlock,
        ProcessSmaBlock,
        ParameterizeSmaBlock,
    ]
    res = Flow.initialize(params=PARAMS).then(blocks)
    params = res.block_glue["parameterize_sma"].params
    assert params["sma_short_diff"] == 0.010209216905010062
    assert params["sma_medium_diff"] == 0.03439245289564408
    assert params["sma_long_diff"] == 0.04131490065439989
    assert params["sma_long_short"] == 0.03143091563893313
    assert params["sma_long_medium"] == 0.0071620089215007
    assert params["sma_impact"] == 5e-05

    params = Flow.from_json(params_list=PARAMS_LIST).block_glue["parameterize_sma"].params
    assert params["sma_short_diff"] == 0.010209216905010062
    assert params["sma_medium_diff"] == 0.03439245289564408
    assert params["sma_long_diff"] == 0.04131490065439989
    assert params["sma_long_short"] == 0.03143091563893313
    assert params["sma_long_medium"] == 0.0071620089215007
    assert params["sma_impact"] == 5e-05

    blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
        ProcessSmaBlock,
        ParameterizeSmaBlock,
    ]
    res = Flow.initialize(params=PARAMS2).then(blocks)
    params = res.block_glue["parameterize_sma"].params
    assert params["sma_short_diff"] == 0.010209216905010062
    assert params["sma_medium_diff"] == 0.03439245289564408
    assert params["sma_long_diff"] == 0.04131490065439989
    assert params["sma_long_short"] == 0.03143091563893313
    assert params["sma_long_medium"] == 0.0071620089215007
    assert params["sma_impact"] == 5e-05

    params = Flow.from_json(params_list=PARAMS_LIST2).block_glue["parameterize_sma"].params
    assert params["sma_short_diff"] == 0.010209216905010062
    assert params["sma_medium_diff"] == 0.03439245289564408
    assert params["sma_long_diff"] == 0.04131490065439989
    assert params["sma_long_short"] == 0.03143091563893313
    assert params["sma_long_medium"] == 0.0071620089215007
    assert params["sma_impact"] == 5e-05


def test_block_parameterize_macd():
    blocks = [
        ReadExampleBlock,
        DefaultPreProcessBlock,
        ProcessMacdBlock,
        ParameterizeMacdBlock,
    ]
    res = Flow.initialize(params=PARAMS).then(blocks)
    params = res.block_glue["parameterize_macd"].params
    assert params["signal"] == -12.860986277017133
    assert params["histogram"] == -2.1950264386049145
    assert params["macd_impact"] == -0.0

    params = Flow.from_json(params_list=PARAMS_LIST).block_glue["parameterize_macd"].params
    assert params["signal"] == -12.860986277017133
    assert params["histogram"] == -2.1950264386049145
    assert params["macd_impact"] == -0.0

    blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
        ProcessMacdBlock,
        ParameterizeMacdBlock,
    ]
    res = Flow.initialize(params=PARAMS2).then(blocks)
    params = res.block_glue["parameterize_macd"].params
    assert params["signal"] == -12.860986277017133
    assert params["histogram"] == -2.1950264386049145
    assert params["macd_impact"] == -0.0


def test_block_parameterize_adx():
    blocks = [
        ReadExampleBlock,
        DefaultPreProcessBlock,
        ProcessAdxBlock,
        ParameterizeAdxBlock,
    ]
    res = Flow.initialize(params=PARAMS).then(blocks)
    params = res.block_glue["parameterize_adx"].params
    assert params["adx_dx"] == 1.3205088401450518
    assert params["adx_adx"] == 67.8193682475764
    assert params["adx_adxr"] == 49.23566585844706
    assert params["adx_impact"] == 0.0

    params = Flow.from_json(params_list=PARAMS_LIST).block_glue["parameterize_adx"].params
    assert params["adx_dx"] == 1.3205088401450518
    assert params["adx_adx"] == 67.8193682475764
    assert params["adx_adxr"] == 49.23566585844706
    assert params["adx_impact"] == 0.0

    blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
        ProcessAdxBlock,
        ParameterizeAdxBlock,
    ]
    res = Flow.initialize(params=PARAMS2).then(blocks)
    params = res.block_glue["parameterize_adx"].params
    assert params["adx_dx"] == 1.3205088401450518
    assert params["adx_adx"] == 67.8193682475764
    assert params["adx_adxr"] == 49.23566585844706
    assert params["adx_impact"] == 0.0


def test_block_parameterize_bollinger_bands():
    blocks = [
        ReadExampleBlock,
        DefaultPreProcessBlock,
        ProcessBollingerBandsBlock,
        ParameterizeBollingerBandsBlock,
    ]
    res = Flow.initialize(params=PARAMS).then(blocks)
    params = res.block_glue["parameterize_bollinger_bands"].params
    assert params["upper_1_sigma"] == 1043.6506512061828
    assert params["lower_1_sigma"] == 1025.1826821271504
    assert params["upper_2_sigma"] == 1052.884635745699
    assert params["lower_2_sigma"] == 1015.9486975876343
    assert params["bollinger_bands_impact"] == -0.96299

    params = Flow.from_json(params_list=PARAMS_LIST).block_glue["parameterize_bollinger_bands"].params
    assert params["upper_1_sigma"] == 1043.6506512061828
    assert params["lower_1_sigma"] == 1025.1826821271504
    assert params["upper_2_sigma"] == 1052.884635745699
    assert params["lower_2_sigma"] == 1015.9486975876343
    assert params["bollinger_bands_impact"] == -0.96299

    blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
        ProcessBollingerBandsBlock,
        ParameterizeBollingerBandsBlock,
    ]
    res = Flow.initialize(params=PARAMS2).then(blocks)
    params = res.block_glue["parameterize_bollinger_bands"].params
    assert params["upper_1_sigma"] == 1043.6506512061828
    assert params["lower_1_sigma"] == 1025.1826821271504
    assert params["upper_2_sigma"] == 1052.884635745699
    assert params["lower_2_sigma"] == 1015.9486975876343
    assert params["bollinger_bands_impact"] == -0.96299


def test_block_parameterize_momentum():
    blocks = [
        ReadExampleBlock,
        DefaultPreProcessBlock,
        ProcessMomentumBlock,
        ParameterizeMomentumBlock,
    ]
    res = Flow.initialize(params=PARAMS).then(blocks)
    params = res.block_glue["parameterize_momentum"].params
    assert params["momentum_impact"] == 0.0

    params = Flow.from_json(params_list=PARAMS_LIST).block_glue["parameterize_momentum"].params
    assert params["momentum_impact"] == 0.0

    blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
        ProcessMomentumBlock,
        ParameterizeMomentumBlock,
    ]
    res = Flow.initialize(params=PARAMS2).then(blocks)
    params = res.block_glue["parameterize_momentum"].params
    assert params["momentum_impact"] == 0.0

    params = Flow.from_json(params_list=PARAMS_LIST2).block_glue["parameterize_momentum"].params
    assert params["momentum_impact"] == 0.0


def test_block_parameterize_psycho_logical():
    blocks = [
        ReadExampleBlock,
        DefaultPreProcessBlock,
        ProcessPsychoLogicalBlock,
        ParameterizePsychoLogicalBlock,
    ]
    res = Flow.initialize(params=PARAMS).then(blocks)
    params = res.block_glue["parameterize_psycho_logical"].params
    assert params["psycho_line"] == 0.2222222222222222
    assert params["psycho_logical_impact"] == 2.95925

    params = Flow.from_json(params_list=PARAMS_LIST).block_glue["parameterize_psycho_logical"].params
    assert params["psycho_line"] == 0.2222222222222222
    assert params["psycho_logical_impact"] == 2.95925

    blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
        ProcessPsychoLogicalBlock,
        ParameterizePsychoLogicalBlock,
    ]
    res = Flow.initialize(params=PARAMS2).then(blocks)
    params = res.block_glue["parameterize_psycho_logical"].params
    assert params["psycho_line"] == 0.2222222222222222
    assert params["psycho_logical_impact"] == 2.95925

    params = Flow.from_json(params_list=PARAMS_LIST2).block_glue["parameterize_psycho_logical"].params
    assert params["psycho_line"] == 0.2222222222222222
    assert params["psycho_logical_impact"] == 2.95925


def test_block_parameterize_stochastics():
    blocks = [
        ReadExampleBlock,
        DefaultPreProcessBlock,
        ProcessStochasticsBlock,
        ParameterizeStochasticsBlock,
    ]
    res = Flow.initialize(params=PARAMS).then(blocks)
    params = res.block_glue["parameterize_stochastics"].params
    assert params["stochastics_k"] == 97.3015873015873
    assert params["stochastics_d"] == 93.9153439153439
    assert params["stochastics_sd"] == 84.23330813807003
    assert params["stochastics_impact"] == -0.48406

    params = Flow.from_json(params_list=PARAMS_LIST).block_glue["parameterize_stochastics"].params
    assert params["stochastics_k"] == 97.3015873015873
    assert params["stochastics_d"] == 93.9153439153439
    assert params["stochastics_sd"] == 84.23330813807003
    assert params["stochastics_impact"] == -0.48406

    blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
        ProcessStochasticsBlock,
        ParameterizeStochasticsBlock,
    ]
    res = Flow.initialize(params=PARAMS2).then(blocks)
    params = res.block_glue["parameterize_stochastics"].params
    assert params["stochastics_k"] == 97.3015873015873
    assert params["stochastics_d"] == 93.9153439153439
    assert params["stochastics_sd"] == 84.23330813807003
    assert params["stochastics_impact"] == -0.48406

    params = Flow.from_json(params_list=PARAMS_LIST2).block_glue["parameterize_stochastics"].params
    assert params["stochastics_k"] == 97.3015873015873
    assert params["stochastics_d"] == 93.9153439153439
    assert params["stochastics_sd"] == 84.23330813807003
    assert params["stochastics_impact"] == -0.48406


def test_block_parameterize_volatility():
    blocks = [
        ReadExampleBlock,
        DefaultPreProcessBlock,
        ParameterizeVolatilityBlock,
    ]
    res = Flow.initialize(params=PARAMS).then(blocks)
    params = res.block_glue["parameterize_volatility"].params
    assert params["volatility"] == 0.015477474132778526
    assert params["close_volatility"] == 1188.063003315964

    params = Flow.from_json(params_list=PARAMS_LIST).block_glue["parameterize_volatility"].params
    assert params["volatility"] == 0.015477474132778526
    assert params["close_volatility"] == 1188.063003315964

    blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
        ParameterizeVolatilityBlock,
    ]
    res = Flow.initialize(params=PARAMS2).then(blocks)
    params = res.block_glue["parameterize_volatility"].params
    assert params["volatility"] == 0.015477474132778526
    assert params["close_volatility"] == 1188.063003315964

    params = Flow.from_json(params_list=PARAMS_LIST2).block_glue["parameterize_volatility"].params
    assert params["volatility"] == 0.015477474132778526
    assert params["close_volatility"] == 1188.063003315964


def test_block_parameterize_pct_change():
    blocks = [
        ReadExampleBlock,
        DefaultPreProcessBlock,
        ParameterizePctChangeBlock,
    ]
    res = Flow.initialize(params=PARAMS).then(blocks)
    params = res.block_glue["parameterize_pct_change"].params
    assert params["pct_05"] == -0.004500275483459349
    assert params["pct_10"] == -0.009220390832081973
    assert params["pct_20"] == -0.01581898346743425
    assert params["pct_30"] == -0.010848218441679503
    assert params["pct_40"] == -0.0048062684235296756

    params = Flow.from_json(params_list=PARAMS_LIST).block_glue["parameterize_pct_change"].params
    assert params["pct_05"] == -0.004500275483459349
    assert params["pct_10"] == -0.009220390832081973
    assert params["pct_20"] == -0.01581898346743425
    assert params["pct_30"] == -0.010848218441679503
    assert params["pct_40"] == -0.0048062684235296756

    blocks = [
        ReadSqlite3Block,
        DefaultPreProcessBlock,
        ParameterizePctChangeBlock,
    ]
    res = Flow.initialize(params=PARAMS2).then(blocks)
    params = res.block_glue["parameterize_pct_change"].params
    assert params["pct_05"] == -0.004500275483459349
    assert params["pct_10"] == -0.009220390832081973
    assert params["pct_20"] == -0.01581898346743425
    assert params["pct_30"] == -0.010848218441679503
    assert params["pct_40"] == -0.0048062684235296756

    params = Flow.from_json(params_list=PARAMS_LIST2).block_glue["parameterize_pct_change"].params
    assert params["pct_05"] == -0.004500275483459349
    assert params["pct_10"] == -0.009220390832081973
    assert params["pct_20"] == -0.01581898346743425
    assert params["pct_30"] == -0.010848218441679503
    assert params["pct_40"] == -0.0048062684235296756
