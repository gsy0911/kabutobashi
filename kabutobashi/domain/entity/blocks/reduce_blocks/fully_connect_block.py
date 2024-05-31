from ..decorator import block





@dataclass(frozen=True)
class FullyConnectBlockInput(IBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        block_outputs = block_glue.block_outputs
        block_outputs_keys = block_outputs.keys()
        # impact
        sma_impact = 0
        if "parameterize_sma" in block_outputs_keys:
            if block_outputs["parameterize_sma"].params is None:
                raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
            sma_impact = block_outputs["parameterize_sma"].params["sma_impact"]
        macd_impact = 0
        if "parameterize_macd" in block_outputs_keys:
            if block_outputs["parameterize_macd"].params is None:
                raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
            macd_impact = block_outputs["parameterize_macd"].params["macd_impact"]
        adx_impact = 0
        if "parameterize_adx" in block_outputs_keys:
            if block_outputs["parameterize_adx"].params is None:
                raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
            adx_impact = block_outputs["parameterize_adx"].params["adx_impact"]
        momentum_impact = 0
        if "parameterize_momentum" in block_outputs_keys:
            if block_outputs["parameterize_momentum"].params is None:
                raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
            momentum_impact = block_outputs["parameterize_momentum"].params["momentum_impact"]
        bollinger_bands_impact = 0
        if "parameterize_bollinger_bands" in block_outputs_keys:
            if block_outputs["parameterize_bollinger_bands"].params is None:
                raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
            bollinger_bands_impact = block_outputs["parameterize_bollinger_bands"].params["bollinger_bands_impact"]
        psycho_logical_impact = 0
        if "parameterize_psycho_logical" in block_outputs_keys:
            if block_outputs["parameterize_psycho_logical"].params is None:
                raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
            psycho_logical_impact = block_outputs["parameterize_psycho_logical"].params["psycho_logical_impact"]
        stochastics_impact = 0
        if "parameterize_stochastics" in block_outputs_keys:
            if block_outputs["parameterize_stochastics"].params is None:
                raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
            stochastics_impact = block_outputs["parameterize_stochastics"].params["stochastics_impact"]
        # ratio
        if block_glue.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        input_params = block_glue.params.get("fully_connect", {})
        sma_impact_ratio = input_params.get("sma_impact_ratio", 0.1)
        macd_impact_ratio = input_params.get("macd_impact_ratio", 0.1)
        adx_impact_ratio = input_params.get("adx_impact_ratio", 0.1)
        bollinger_bands_impact_ratio = input_params.get("bollinger_bands_impact_ratio", 0.1)
        momentum_impact_ratio = input_params.get("momentum_impact_ratio", 0.1)
        psycho_logical_impact_ratio = input_params.get("psycho_logical_impact_ratio", 0.1)
        stochastics_impact_ratio = input_params.get("stochastics_impact_ratio", 0.1)
        return FullyConnectBlockInput(
            series=None,
            params={
                "sma_impact": sma_impact,
                "macd_impact": macd_impact,
                "adx_impact": adx_impact,
                "bollinger_bands_impact": bollinger_bands_impact,
                "momentum_impact": momentum_impact,
                "psycho_logical_impact": psycho_logical_impact,
                "stochastics_impact": stochastics_impact,
                "sma_impact_ratio": sma_impact_ratio,
                "macd_impact_ratio": macd_impact_ratio,
                "adx_impact_ratio": adx_impact_ratio,
                "bollinger_bands_impact_ratio": bollinger_bands_impact_ratio,
                "momentum_impact_ratio": momentum_impact_ratio,
                "psycho_logical_impact_ratio": psycho_logical_impact_ratio,
                "stochastics_impact_ratio": stochastics_impact_ratio,
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

@block(block_name="fully_connect")
class FullyConnectBlock:

    def _process(self) -> dict:
        reduced_params = {
            "impact": self.params["sma_impact"] * self.params["sma_impact_ratio"]
            + self.params["macd_impact"] * self.params["macd_impact_ratio"]
            + self.params["adx_impact"] * self.params["adx_impact_ratio"]
            + self.params["bollinger_bands_impact"] * self.params["bollinger_bands_impact_ratio"]
            + self.params["momentum_impact"] * self.params["momentum_impact_ratio"]
            + self.params["psycho_logical_impact"] * self.params["psycho_logical_impact_ratio"]
            + self.params["stochastics_impact"] * self.params["stochastics_impact_ratio"]
        }
        return reduced_params
