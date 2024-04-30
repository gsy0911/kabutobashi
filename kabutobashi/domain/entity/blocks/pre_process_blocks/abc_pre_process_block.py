from abc import ABC
from dataclasses import dataclass, replace
from typing import Optional

from injector import Injector, inject
from overrides import override

from ..abc_block import BlockGlue, IBlock, IBlockInput, IBlockOutput


@dataclass(frozen=True)
class IPreProcessBlockInput(IBlockInput, ABC):
    pass


@dataclass(frozen=True)
class IPreProcessBlockOutput(IBlockOutput, ABC):
    pass


@inject
@dataclass(frozen=True)
class IPreProcessBlock(IBlock, ABC):
    """
    Blocks for pre-process the data
    """

    block_input: Optional[IPreProcessBlockInput]

    @classmethod
    @override
    def glue(cls, glue: "BlockGlue") -> "BlockGlue":
        block = Injector(cls._configure).get(cls)
        updated_block = replace(cls(block_input=None), block_input=block.block_input.of(block_glue=glue))
        block_output = updated_block.process()
        updated_glue = glue.update(block_output=block_output)
        # update glue-series, to apply series
        updated_glue = replace(updated_glue, series=block_output.series)
        return updated_glue
