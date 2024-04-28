from dataclasses import dataclass, replace
from typing import List, Optional, Union

from kabutobashi.domain.services.blocks.abc_block import BlockGlue, IBlock


@dataclass(frozen=True)
class Flow:
    block_glue: BlockGlue

    @staticmethod
    def initialize(params: dict) -> "Flow":
        glue = BlockGlue(series=None, params=params)
        return Flow(block_glue=glue)

    def then(self, block: Union[IBlock, List[IBlock]]) -> "Flow":
        if type(block) is list:
            flow = self
            glue = self.block_glue
            for v in block:
                glue = v.glue(glue=glue)
                flow = replace(flow, block_glue=glue)
            return flow
        else:
            new_glue = block.glue(glue=self.block_glue)
            return replace(self, block_glue=new_glue)

    def reduce(self, block: IBlock) -> BlockGlue:
        new_glue = block.glue(glue=self.block_glue)
        return new_glue
