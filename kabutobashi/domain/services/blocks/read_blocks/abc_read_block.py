from abc import ABC, abstractmethod

import pandas as pd

from ..abc_block import IBlock, IBlockInput, IBlockOutput


class IReadBlock(IBlock, ABC):
    pass
