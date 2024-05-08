from dataclasses import dataclass

import pandas as pd
from injector import Binder, inject

from kabutobashi.domain.errors import KabutobashiBlockInstanceMismatchError, KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue, IBlockInput
from .abc_process_block import IProcessBlock, IProcessBlockInput, IProcessBlockOutput


@dataclass(frozen=True)
class ProcessPsychoLogicalBlockInput(IProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        input_params = block_glue.params.get("process_macd", {})
        psycho_term = input_params.get("psycho_term", 12)
        upper_threshold = input_params.get("upper_threshold", 0.75)
        lower_threshold = input_params.get("lower_threshold", 0.25)
        return cls(
            series=block_glue.series,
            params={
                "psycho_term": psycho_term,
                "upper_threshold": upper_threshold,
                "lower_threshold": lower_threshold,
            },
        )

    def _validate(self):
        pass


@dataclass(frozen=True)
class ProcessPsychoLogicalBlockOutput(IProcessBlockOutput):
    block_name: str = "process_psycho_logical"

    def _validate(self):
        pass


@inject
@dataclass(frozen=True)
class ProcessPsychoLogicalBlock(IProcessBlock):

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:
        params = self.block_input.params
        if params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        psycho_term = params["psycho_term"]
        upper_threshold = params["upper_threshold"]
        lower_threshold = params["lower_threshold"]

        df_ = df.copy()
        df_["shift_close"] = df_["close"].shift(1)
        df_ = df_.fillna(0)
        df_["diff"] = df_.apply(lambda x: x["close"] - x["shift_close"], axis=1)

        df_["is_raise"] = df_["diff"].apply(lambda x: 1 if x > 0 else 0)

        df_["psycho_sum"] = df_["is_raise"].rolling(psycho_term).sum()
        df_["psycho_line"] = df_["psycho_sum"].apply(lambda x: x / psycho_term)

        df_["bought_too_much"] = df_["psycho_line"].apply(lambda x: 1 if x > upper_threshold else 0)
        df_["sold_too_much"] = df_["psycho_line"].apply(lambda x: 1 if x < lower_threshold else 0)
        return df_

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df["buy_signal"] = df["sold_too_much"]
        df["sell_signal"] = df["bought_too_much"]
        return df

    def _process(self) -> ProcessPsychoLogicalBlockOutput:
        if not isinstance(self.block_input, ProcessPsychoLogicalBlockInput):
            raise KabutobashiBlockInstanceMismatchError()

        applied_df = self._apply(df=self.block_input.series)
        signal_df = self._signal(df=applied_df)
        required_columns = ["psycho_line", "bought_too_much", "sold_too_much", "buy_signal", "sell_signal"]
        return ProcessPsychoLogicalBlockOutput.of(series=signal_df[required_columns], params=None)

    @classmethod
    def _configure(cls, binder: Binder) -> None:
        binder.bind(IProcessBlockInput, to=ProcessPsychoLogicalBlockInput)
