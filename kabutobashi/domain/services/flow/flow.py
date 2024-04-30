from dataclasses import dataclass, replace
from typing import List, Union

from kabutobashi.domain.entity.blocks.abc_block import BlockGlue, IBlock
from kabutobashi.domain.entity.blocks.hub_block import FromJsonBlock


@dataclass(frozen=True)
class Flow:
    block_glue: BlockGlue

    @staticmethod
    def from_json(params_list: List[dict]) -> "Flow":
        flow_params = {}
        block_list = []
        for params in params_list:
            block, block_params = FromJsonBlock.from_json(params).get()
            block_list.append(block)
            flow_params.update(block_params)
        return Flow.initialize(params=flow_params).then(block=block_list)

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
