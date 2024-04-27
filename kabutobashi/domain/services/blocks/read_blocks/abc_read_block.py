from injector import inject
from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from ..abc_block import IBlock, IBlockInput, IBlockOutput, ILayer


class IReadBlockInput(IBlockInput, ABC):
    pass


class IReadBlock(IBlock, ABC):
    pass


@inject
@dataclass(frozen=True)
class IReadLayer(ILayer, ABC):
    block_input: IReadBlockInput
    block: IReadBlock
