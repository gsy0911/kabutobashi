from dataclasses import dataclass

import pandas as pd

from kabutobashi.domain.errors import KabutobashiBlockParamsIsNoneError

from ..abc_block import BlockGlue
from ..decorator import block
from .abc_process_block import IProcessBlockInput, IProcessBlockOutput, cross


@dataclass(frozen=True)
class ProcessMomentumBlockInput(IProcessBlockInput):

    @classmethod
    def of(cls, block_glue: "BlockGlue"):
        if block_glue.params is None:
            raise KabutobashiBlockParamsIsNoneError("Block inputs must have 'params' params")
        input_params = block_glue.params.get("process_momentum", {})
        term = input_params.get("term", 12)
        return cls(
            series=block_glue.series,
            params={
                "term": term,
            },
        )

    def _validate(self):
        pass


@dataclass(frozen=True)
class ProcessMomentumBlockOutput(IProcessBlockOutput):
    block_name: str = "process_momentum"

    def _validate(self):
        pass


@block(block_name="process_momentum", pre_condition_block_name="read_example")
class ProcessMomentumBlock:
    series: pd.DataFrame
    term: int = 12

    def _apply(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df.assign(
            momentum=df["close"].shift(10),
        ).fillna(0)
        df = df.assign(sma_momentum=lambda x: x["momentum"].rolling(self.term).mean())
        return df

    def _signal(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.join(cross(df["sma_momentum"]))
        df = df.rename(columns={"to_plus": "buy_signal", "to_minus": "sell_signal"})
        return df

    def _process(self) -> pd.DataFrame:

        applied_df = self._apply(df=self.series)
        signal_df = self._signal(df=applied_df)
        required_columns = ["momentum", "sma_momentum", "buy_signal", "sell_signal"]
        return signal_df[required_columns]
