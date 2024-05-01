from dataclasses import dataclass

from injector import Binder, inject

from ..abc_block import BlockGlue, IBlock, IBlockInput, IBlockOutput


@dataclass(frozen=True)
class FullyConnectBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        block_outputs = block_glue.block_outputs
        input_params = block_glue.params.get("fully_connect", {})
        sma_impact_ratio = input_params.get("sma_impact_ratio", 0.1)
        macd_impact_ratio = input_params.get("macd_impact_ratio", 0.1)
        adx_impact_ratio = input_params.get("adx_impact_ratio", 0.1)
        bollinger_bands_impact_ratio = input_params.get("bollinger_bands_impact_ratio", 0.1)
        return FullyConnectBlockInput(
            series=None,
            params={
                "sma_impact": block_outputs["parameterize_sma"].params["sma_impact"],
                "macd_impact": block_outputs["parameterize_macd"].params["macd_impact"],
                "adx_impact": block_outputs["parameterize_adx"].params["adx_impact"],
                "bollinger_bands_impact": block_outputs["parameterize_bollinger_bands"].params[
                    "bollinger_bands_impact"
                ],
                "sma_impact_ratio": sma_impact_ratio,
                "macd_impact_ratio": macd_impact_ratio,
                "adx_impact_ratio": adx_impact_ratio,
                "bollinger_bands_impact_ratio": bollinger_bands_impact_ratio,
            },
        )

    def _validate(self):
        if self.params:
            keys = self.params.keys()
            assert "sma_impact" in keys, "FullyConnectBlockOutput must have 'sma_impact' column"
            assert "sma_impact_ratio" in keys, "FullyConnectBlockOutput must have 'sma_impact_ratio' column"
            assert 0 <= self.params["sma_impact_ratio"] <= 1, "'sma_impact_ratio' must be between 0 and 1"
            assert "macd_impact" in keys, "FullyConnectBlockOutput must have 'macd_impact' column"
            assert "macd_impact_ratio" in keys, "FullyConnectBlockOutput must have 'macd_impact_ratio' column"
            assert 0 <= self.params["macd_impact_ratio"] <= 1, "'macd_impact_ratio' must be between 0 and 1"
            assert "adx_impact" in keys, "FullyConnectBlockOutput must have 'adx_impact' column"
            assert "adx_impact_ratio" in keys, "FullyConnectBlockOutput must have 'adx_impact_ratio' column"
            assert 0 <= self.params["adx_impact_ratio"] <= 1, "'adx_impact_ratio' must be between 0 and 1"


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
            "impact": params["sma_impact"] * params["sma_impact_ratio"]
            + params["macd_impact"] * params["macd_impact_ratio"]
            + params["adx_impact"] * params["adx_impact_ratio"]
        }
        return FullyConnectBlockOutput.of(
            series=None,
            params=reduced_params,
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IBlockInput, to=FullyConnectBlockInput)
