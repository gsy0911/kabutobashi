from abc import ABC
from dataclasses import dataclass

from injector import inject

from ..abc_block import IBlock, IBlockInput, IBlockOutput

__all__ = ["IExtractBlock", "IExtractBlockInput", "IExtractBlockOutput"]


@dataclass(frozen=True)
class IExtractBlockInput(IBlockInput, ABC):
    pass


@dataclass(frozen=True)
class IExtractBlockOutput(IBlockOutput, ABC):
    pass


@inject
@dataclass(frozen=True)
class IExtractBlock(IBlock, ABC):
    block_input: IBlockInput
