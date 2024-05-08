from dataclasses import dataclass

import pandas as pd
from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue
from .abc_process_block import IProcessBlock, IProcessBlockInput, IProcessBlockOutput

__all__ = ["ProcessBollingerBandsBlock"]


@dataclass(frozen=True)
class ProcessBollingerBandsBlockInput(IProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        if block_glue.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        input_params = block_glue.params.get("process_bollinger_bands", {})
        band_term = input_params.get("band_term", 12)
        continuity_term = input_params.get("continuity_term", 10)
        return cls(
            series=block_glue.series,
            params={
                "band_term": band_term,
                "continuity_term": continuity_term,
            },
        )

    def _validate(self):
        pass


@dataclass(frozen=True)
class ProcessBollingerBandsBlockOutput(IProcessBlockOutput):
    block_name: str = "process_bollinger_bands"

    def _validate(self):
        pass


@inject
@dataclass(frozen=True)
class ProcessBollingerBandsBlock(IProcessBlock):

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:
        params = self.block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        band_term = params["band_term"]

        df = df.assign(mean=df["close"].rolling(band_term).mean(), std=df["close"].rolling(band_term).std())
        df = df.assign(
            upper_1_sigma=df.apply(lambda x: x["mean"] + x["std"] * 1, axis=1),
            lower_1_sigma=df.apply(lambda x: x["mean"] - x["std"] * 1, axis=1),
            upper_2_sigma=df.apply(lambda x: x["mean"] + x["std"] * 2, axis=1),
            lower_2_sigma=df.apply(lambda x: x["mean"] - x["std"] * 2, axis=1),
            upper_3_sigma=df.apply(lambda x: x["mean"] + x["std"] * 3, axis=1),
            lower_3_sigma=df.apply(lambda x: x["mean"] - x["std"] * 3, axis=1),
        )
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        params = self.block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        continuity_term = params["continuity_term"]

        df = df.assign(
            over_upper=df.apply(lambda x: 1 if x["close"] > x["upper_2_sigma"] else 0, axis=1),
            over_lower=df.apply(lambda x: 1 if x["close"] < x["lower_2_sigma"] else 0, axis=1),
            over_upper_continuity=lambda x: x["over_upper"].rolling(continuity_term).sum(),
            over_lower_continuity=lambda x: x["over_lower"].rolling(continuity_term).sum(),
        )

        df["buy_signal"] = df["over_upper"].apply(lambda x: 1 if x > 0 else 0)
        df["sell_signal"] = df["over_lower"].apply(lambda x: 1 if x > 0 else 0)
        return df

    def _process(self) -> ProcessBollingerBandsBlockOutput:
        if not isinstance(self.block_input, ProcessBollingerBandsBlockInput):
            raise KabutobashiBlockInstanceMismatchError()

        applied_df = self._apply(df=self.block_input.series)
        signal_df = self._signal(df=applied_df)
        required_columns = [
            "upper_1_sigma",
            "lower_1_sigma",
            "upper_2_sigma",
            "lower_2_sigma",
            "upper_3_sigma",
            "lower_3_sigma",
            "over_upper_continuity",
            "over_lower_continuity",
        ]
        return ProcessBollingerBandsBlockOutput.of(
            series=signal_df[required_columns],
            params=self.block_input.params,
        )

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IProcessBlockInput, to=ProcessBollingerBandsBlockInput)  # type: ignore[type-abstract]
