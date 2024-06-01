from typing import Tuple

from pydantic import BaseModel

from .abc_block import IBlock


class FromJsonBlock(BaseModel):
    id_: str
    block_name: str
    sequence_no: int
    params: dict

    @staticmethod
    def from_json(params: dict) -> "FromJsonBlock":
        block_name = params["block_name"]
        return FromJsonBlock(
            id_=params["id"], block_name=block_name, sequence_no=params["sequence_no"], params=params.get("params", {})
        )

    def get(self) -> Tuple[type[IBlock], dict]:
        # TODO ここのブロックの取得方法をメタプログラミングっぽく
        from .crawl_blocks import CrawlStockInfoBlock, CrawlStockInfoMultipleDaysBlock, CrawlStockIpoBlock
        from .extract_blocks import ExtractStockInfoBlock, ExtractStockInfoMultipleDaysBlock, ExtractStockIpoBlock
        from .parameterize_blocks import (
            ParameterizeAdxBlock,
            ParameterizeBollingerBandsBlock,
            ParameterizeMacdBlock,
            ParameterizeMomentumBlock,
            ParameterizePsychoLogicalBlock,
            ParameterizeSmaBlock,
            ParameterizeStochasticsBlock,
        )
        from .pre_process_blocks import DefaultPreProcessBlock
        from .process_blocks import (
            ProcessAdxBlock,
            ProcessBollingerBandsBlock,
            ProcessMacdBlock,
            ProcessMomentumBlock,
            ProcessPsychoLogicalBlock,
            ProcessSmaBlock,
            ProcessStochasticsBlock,
        )
        from .read_blocks import ReadExampleBlock

        if self.block_name == "read_example":
            return ReadExampleBlock, {self.block_name: self.params}
        # pre-process
        elif self.block_name == "default_pre_process":
            return DefaultPreProcessBlock, {self.block_name: self.params}
        # process
        elif self.block_name == "process_sma":
            return ProcessSmaBlock, {self.block_name: self.params}
        elif self.block_name == "parameterize_sma":
            return ParameterizeSmaBlock, {self.block_name: self.params}
        elif self.block_name == "process_macd":
            return ProcessMacdBlock, {self.block_name: self.params}
        elif self.block_name == "parameterize_macd":
            return ParameterizeMacdBlock, {self.block_name: self.params}
        elif self.block_name == "process_adx":
            return ProcessAdxBlock, {self.block_name: self.params}
        elif self.block_name == "parameterize_adx":
            return ParameterizeAdxBlock, {self.block_name: self.params}
        elif self.block_name == "process_bollinger_bands":
            return ProcessBollingerBandsBlock, {self.block_name: self.params}
        elif self.block_name == "parameterize_bollinger_bands":
            return ParameterizeBollingerBandsBlock, {self.block_name: self.params}
        elif self.block_name == "process_momentum":
            return ProcessMomentumBlock, {self.block_name: self.params}
        elif self.block_name == "parameterize_momentum":
            return ParameterizeMomentumBlock, {self.block_name: self.params}
        elif self.block_name == "process_psycho_logical":
            return ProcessPsychoLogicalBlock, {self.block_name: self.params}
        elif self.block_name == "parameterize_psycho_logical":
            return ParameterizePsychoLogicalBlock, {self.block_name: self.params}
        elif self.block_name == "process_stochastics":
            return ProcessStochasticsBlock, {self.block_name: self.params}
        elif self.block_name == "parameterize_stochastics":
            return ParameterizeStochasticsBlock, {self.block_name: self.params}
        # crawl
        elif self.block_name == "crawl_stock_info":
            return CrawlStockInfoBlock, {self.block_name: self.params}
        elif self.block_name == "crawl_stock_info_multiple_days":
            return CrawlStockInfoMultipleDaysBlock, {self.block_name: self.params}
        elif self.block_name == "crawl_stock_ipo":
            return CrawlStockIpoBlock, {self.block_name: self.params}
        # extract
        elif self.block_name == "extract_stock_info":
            return ExtractStockInfoBlock, {self.block_name: self.params}
        elif self.block_name == "extract_stock_info_multiple_days":
            return ExtractStockInfoMultipleDaysBlock, {self.block_name: self.params}
        elif self.block_name == "extract_stock_ipo":
            return ExtractStockIpoBlock, {self.block_name: self.params}
        raise ValueError()
