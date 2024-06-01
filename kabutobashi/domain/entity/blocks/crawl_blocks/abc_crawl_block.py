import httpx

from kabutobashi.domain.errors import KabutobashiPageError
from kabutobashi.domain.values import UserAgent

__all__ = ["from_url"]


def from_url(url: str) -> str:
    user_agent = UserAgent.get_user_agent_header()
    r = httpx.get(url, headers=user_agent)

    if r.status_code != 200:
        raise KabutobashiPageError(url=url)

    return r.text
