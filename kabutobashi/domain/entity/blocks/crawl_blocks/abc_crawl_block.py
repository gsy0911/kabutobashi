from abc import ABC
from dataclasses import dataclass

import httpx
from injector import inject

from kabutobashi.domain.errors import KabutobashiPageError
from kabutobashi.domain.values import UserAgent

from ..abc_block import IBlock, IBlockInput, IBlockOutput

__all__ = ["ICrawlBlock", "ICrawlBlockInput", "ICrawlBlockOutput"]


@dataclass(frozen=True)
class ICrawlBlockInput(IBlockInput, ABC):
    pass


@dataclass(frozen=True)
class ICrawlBlockOutput(IBlockOutput, ABC):
    pass


@inject
@dataclass(frozen=True)
class ICrawlBlock(IBlock, ABC):
    block_input: ICrawlBlockInput

    @staticmethod
    def _from_url(url: str) -> str:
        user_agent = UserAgent.get_user_agent_header()
        r = httpx.get(url, headers=user_agent)

        if r.status_code != 200:
            raise KabutobashiPageError(url=url)

        return r.text
