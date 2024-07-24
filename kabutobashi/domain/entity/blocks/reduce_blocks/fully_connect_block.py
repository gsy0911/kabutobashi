from typing import Tuple

import pandas as pd

from ..decorator import block


@block(
    block_name="fully_connect",
    params_required_keys=[
        "code",
        "dt",
        "sma_impact",
        "macd_impact",
        "adx_impact",
        "bollinger_bands_impact",
        "momentum_impact",
        "psycho_logical_impact",
        "stochastics_impact",
    ],
)
class FullyConnectBlock:

    def _process(self) -> Tuple[pd.DataFrame, dict]:
        impact = (
            self.params["sma_impact"] * self.params.get("sma_impact_ratio", 0.1)
            + self.params["macd_impact"] * self.params.get("macd_impact_ratio", 0.5)
            + self.params["adx_impact"] * self.params.get("adx_impact_ratio", 0.1)
            + self.params["bollinger_bands_impact"] * self.params.get("bollinger_bands_impact_ratio", 0.1)
            + self.params["momentum_impact"] * self.params.get("momentum_impact_ratio", 0.1)
            + self.params["psycho_logical_impact"] * self.params.get("psycho_logical_impact_ratio", 0.1)
            + self.params["stochastics_impact"] * self.params.get("stochastics_impact_ratio", 0.1)
        )
        df = pd.DataFrame.from_dict({"code": [str(self.params["code"])], "dt": [self.params["dt"]], "impact": [impact]})
        return df, {"impact": impact}
