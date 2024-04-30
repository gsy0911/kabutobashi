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

    def get(self) -> Tuple[IBlock, dict]:
        from .parameterize_blocks import ParameterizeMacdBlock, ParameterizeSmaBlock
        from .process_blocks import ProcessMacdBlock, ProcessSmaBlock
        from .read_blocks import ReadExampleBlock

        if self.block_name == "read_example":
            return ReadExampleBlock, {self.block_name: self.params}
        elif self.block_name == "process_sma":
            return ProcessSmaBlock, {self.block_name: self.params}
        elif self.block_name == "parameterize_sma":
            return ParameterizeSmaBlock, {self.block_name: self.params}
        elif self.block_name == "process_macd":
            return ProcessMacdBlock, {self.block_name: self.params}
        elif self.block_name == "parameterize_macd":
            return ParameterizeMacdBlock, {self.block_name: self.params}
