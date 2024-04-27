from abc import ABC
from dataclasses import dataclass

from injector import inject

from ..abc_block import IBlock, IBlockInput


class IReadBlockInput(IBlockInput, ABC):
    pass


@inject
@dataclass(frozen=True)
class IReadBlock(IBlock, ABC):
    block_input: IReadBlockInput
