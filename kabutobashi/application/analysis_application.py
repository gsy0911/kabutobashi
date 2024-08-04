from kabutobashi.domain.entity.blocks.parameterize_blocks import (
    ParameterizeAdxBlock,
    ParameterizeBollingerBandsBlock,
    ParameterizeMacdBlock,
    ParameterizeMomentumBlock,
    ParameterizePsychoLogicalBlock,
    ParameterizeSmaBlock,
    ParameterizeStochasticsBlock,
)
from kabutobashi.domain.entity.blocks.pre_process_blocks import DefaultPreProcessBlock
from kabutobashi.domain.entity.blocks.process_blocks import (
    ProcessAdxBlock,
    ProcessBollingerBandsBlock,
    ProcessMacdBlock,
    ProcessMomentumBlock,
    ProcessPsychoLogicalBlock,
    ProcessSmaBlock,
    ProcessStochasticsBlock,
)
from kabutobashi.domain.entity.blocks.read_blocks import ReadSqlite3Block
from kabutobashi.domain.entity.blocks.reduce_blocks import FullyConnectBlock
from kabutobashi.domain.entity.blocks.write_blocks import WriteImpactSqlite3Block
from kabutobashi.domain.services.flow import Flow


def analysis(code: str, database_dir: str):
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
        FullyConnectBlock,
        WriteImpactSqlite3Block,
    ]

    return Flow.initialize(
        params={
            "read_sqlite3": {"code": code, "database_dir": database_dir},
            "write_impact_sqlite3": {"database_dir": database_dir},
        }
    ).then(blocks)
