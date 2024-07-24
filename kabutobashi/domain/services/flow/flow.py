from dataclasses import dataclass, field, replace
from typing import List, Union

from kabutobashi.domain.entity.blocks.basis_blocks import BlockGlue, BlockOutput, IBlock
from kabutobashi.domain.entity.blocks.decorator import block_from


@dataclass(frozen=True)
class Flow:
    block_glue: BlockGlue

    @staticmethod
    def from_json(params_list: List[dict]) -> "Flow":
        flow_params = {}
        block_list = []
        for params in params_list:
            block = block_from(params["block_name"])
            block_list.append(block)
            flow_params.update({params["block_name"]: params.get("params", {})})
        return Flow.initialize(params=flow_params).then(block=block_list)

    @staticmethod
    def initialize(params: dict) -> "Flow":
        initial_output = BlockOutput(series=None, params=params, block_name="initial_output", execution_order=1)
        glue = BlockGlue(series=None, params=params, block_outputs={"FLOW_INITIAL": initial_output})
        return Flow(block_glue=glue)

    def then(self, block: Union[type[IBlock], List[type[IBlock]]]) -> "Flow":
        if type(block) is list:
            flow = self
            glue: BlockGlue = self.block_glue
            for b in block:
                glue = b.glue(glue=glue)
                flow = replace(flow, block_glue=glue)
            return flow
        else:
            new_glue = block.glue(glue=self.block_glue)
            return replace(self, block_glue=new_glue)

    def reduce(self, block: IBlock) -> BlockGlue:
        new_glue = block.glue(glue=self.block_glue)
        return new_glue


@dataclass(frozen=True)
class FlowPath:
    next_sequence_no: int = field(default=1)
    flow_params_list: list = field(default_factory=list)

    def sma(self) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list
        process = {"id": "process_sma", "block_name": "process_sma", "sequence_no": next_sequence_no, "params": {}}
        parameterize = {
            "id": "parameterize_sma",
            "block_name": "parameterize_sma",
            "sequence_no": next_sequence_no + 1,
            "params": {},
        }
        flow_params_list.extend([process, parameterize])
        return replace(self, next_sequence_no=next_sequence_no + 2, flow_params_list=flow_params_list)

    def macd(self) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list

        process = {"id": "process_macd", "block_name": "process_macd", "sequence_no": next_sequence_no, "params": {}}
        parameterize = {
            "id": "parameterize_macd",
            "block_name": "parameterize_macd",
            "sequence_no": next_sequence_no + 1,
            "params": {},
        }
        flow_params_list.extend([process, parameterize])
        return replace(self, next_sequence_no=next_sequence_no + 2, flow_params_list=flow_params_list)

    def stochastics(self) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list

        process = {
            "id": "process_stochastics",
            "block_name": "process_stochastics",
            "sequence_no": next_sequence_no,
            "params": {},
        }
        parameterize = {
            "id": "parameterize_stochastics",
            "block_name": "parameterize_stochastics",
            "sequence_no": next_sequence_no + 1,
            "params": {},
        }
        flow_params_list.extend([process, parameterize])
        return replace(self, next_sequence_no=next_sequence_no + 2, flow_params_list=flow_params_list)

    def momentum(self) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list

        process = {
            "id": "process_momentum",
            "block_name": "process_momentum",
            "sequence_no": next_sequence_no,
            "params": {},
        }
        parameterize = {
            "id": "parameterize_momentum",
            "block_name": "parameterize_momentum",
            "sequence_no": next_sequence_no + 1,
            "params": {},
        }
        flow_params_list.extend([process, parameterize])
        return replace(self, next_sequence_no=next_sequence_no + 2, flow_params_list=flow_params_list)

    def adx(self) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list

        process = {"id": "process_adx", "block_name": "process_adx", "sequence_no": next_sequence_no, "params": {}}
        parameterize = {
            "id": "parameterize_adx",
            "block_name": "parameterize_adx",
            "sequence_no": next_sequence_no + 1,
            "params": {},
        }
        flow_params_list.extend([process, parameterize])
        return replace(self, next_sequence_no=next_sequence_no + 2, flow_params_list=flow_params_list)

    def psycho_logical(self) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list

        process = {
            "id": "process_psycho_logical",
            "block_name": "process_psycho_logical",
            "sequence_no": next_sequence_no,
            "params": {},
        }
        parameterize = {
            "id": "parameterize_psycho_logical",
            "block_name": "parameterize_psycho_logical",
            "sequence_no": next_sequence_no + 1,
            "params": {},
        }
        flow_params_list.extend([process, parameterize])
        return replace(self, next_sequence_no=next_sequence_no + 2, flow_params_list=flow_params_list)

    def bollinger_bands(self) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list

        process = {
            "id": "process_bollinger_bands",
            "block_name": "process_bollinger_bands",
            "sequence_no": next_sequence_no,
            "params": {},
        }
        parameterize = {
            "id": "parameterize_bollinger_bands",
            "block_name": "parameterize_bollinger_bands",
            "sequence_no": next_sequence_no + 1,
            "params": {},
        }
        flow_params_list.extend([process, parameterize])
        return replace(self, next_sequence_no=next_sequence_no + 2, flow_params_list=flow_params_list)

    def volatility(self) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list

        parameterize = {
            "id": "parameterize_volatility",
            "block_name": "parameterize_volatility",
            "sequence_no": next_sequence_no + 1,
            "params": {},
        }
        flow_params_list.extend([parameterize])
        return replace(self, next_sequence_no=next_sequence_no + 1, flow_params_list=flow_params_list)

    def pct_change(self) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list

        parameterize = {
            "id": "parameterize_pct_change",
            "block_name": "parameterize_pct_change",
            "sequence_no": next_sequence_no + 1,
            "params": {},
        }
        flow_params_list.extend([parameterize])
        return replace(self, next_sequence_no=next_sequence_no + 1, flow_params_list=flow_params_list)

    def read_example(self, code: int) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list
        flow_params_list.append(
            {
                "id": "read_example",
                "block_name": "read_example",
                "sequence_no": next_sequence_no,
                "params": {"code": code},
            }
        )
        return replace(self, next_sequence_no=next_sequence_no + 1, flow_params_list=flow_params_list)

    def read_sqlite3(self, code: int, database_dir) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list
        flow_params_list.append(
            {
                "id": "read_sqlite3",
                "block_name": "read_sqlite3",
                "sequence_no": next_sequence_no,
                "params": {"code": code, "database_dir": database_dir},
            }
        )
        return replace(self, next_sequence_no=next_sequence_no + 1, flow_params_list=flow_params_list)

    def apply_default_pre_process(self) -> "FlowPath":
        next_sequence_no = self.next_sequence_no
        flow_params_list = self.flow_params_list
        flow_params_list.append(
            {"id": "default_pre_process", "block_name": "default_pre_process", "sequence_no": next_sequence_no}
        )
        return replace(self, next_sequence_no=next_sequence_no + 1, flow_params_list=flow_params_list)

    def dumps(self) -> List[dict]:
        return self.flow_params_list

    def execute(self) -> Flow:
        return Flow.from_json(params_list=self.flow_params_list)
