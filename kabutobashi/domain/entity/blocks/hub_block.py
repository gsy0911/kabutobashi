from pydantic import BaseModel

from .abc_block import IBlock


class FromJsonBlock(BaseModel):
    id_: str
    block_name: str
    sequence_no: int

    @staticmethod
    def from_json(params: dict) -> "FromJsonBlock":
        block_name = params["block_name"]
        return FromJsonBlock(
            id_=params["id"],
            block_name=block_name,
            sequence_no=params["sequence_no"],
        )

    def get(self) -> IBlock:
        from .parameterize_blocks import ParameterizeMacdBlock, ParameterizeSmaBlock
        from .process_blocks import ProcessMacdBlock, ProcessSmaBlock
        from .read_blocks import ReadExampleBlock

        if self.block_name == "read_example":
            return ReadExampleBlock
        elif self.block_name == "process_sma":
            return ProcessSmaBlock
        elif self.block_name == "parameterize_sma":
            return ParameterizeSmaBlock
        elif self.block_name == "process_macd":
            return ProcessMacdBlock
        elif self.block_name == "parameterize_macd":
            return ParameterizeMacdBlock
