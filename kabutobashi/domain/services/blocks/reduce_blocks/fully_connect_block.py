from dataclasses import dataclass

from injector import Binder, inject

from ..abc_block import BlockGlue, IBlock, IBlockInput, IBlockOutput


@dataclass(frozen=True)
class FullyConnectBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        block_outputs = block_glue.block_outputs
        processed_sma_series = block_glue.block_outputs["process_sma"].series
        return FullyConnectBlockInput(
            series=None,
            params={
                "sma_impact": block_outputs["parameterize_sma"].params["sma_impact"],
                "macd_impact": block_outputs["parameterize_macd"].params["macd_impact"],
            },
        )

    def _validate(self):
        if self.params:
            keys = self.params.keys()
            assert "sma_impact" in keys, "FullyConnectBlockOutput must have 'sma_impact' column"
            assert "macd_impact" in keys, "FullyConnectBlockOutput must have 'macd_impact' column"


@dataclass(frozen=True)
class FullyConnectBlockOutput(IBlockOutput):
    block_name: str = "fully_connect"

    def _validate(self):
        pass


@inject
@dataclass(frozen=True)
class FullyConnectBlock(IBlock):

    def _process(self, block_input: FullyConnectBlockInput) -> FullyConnectBlockOutput:
        params = block_input.params
        reduced_params = {
            "impact": params["sma_impact"] * 0.1 + params["macd_impact"] * 0.5,
        }
        return FullyConnectBlockOutput.of(
            series=None,
            params=reduced_params,
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IBlockInput, to=FullyConnectBlockInput)
