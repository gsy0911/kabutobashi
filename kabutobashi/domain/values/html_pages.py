from dataclasses import dataclass

import requests  # type: ignore
from bs4 import BeautifulSoup

from kabutobashi.domain.errors import KabutobashiPageError

from .user_agent import UserAgent


@dataclass(frozen=True)
class StockPageHtml:
    """
    id: code & dt
    """

    code: str
    dt: str
    html: str
    page_type: str

    def __post_init__(self):
        assert self.page_type in ["info", "ipo"]

    def to_dict(self) -> dict:
        return {"code": self.code, "dt": self.dt, "html": self.html}

    @staticmethod
    def from_url(url: str, code: str, dt: str, page_type: str) -> "StockPageHtml":
        """
        TODO repositoryを利用するように修正する
        requestsを使って、webからhtmlを取得する
        """
        user_agent = UserAgent.get_user_agent_header()
        r = requests.get(url, headers=user_agent)

        if r.status_code != 200:
            raise KabutobashiPageError(url=url)

        # 日本語に対応
        r.encoding = r.apparent_encoding
        return StockPageHtml(code=code, dt=dt, html=r.text, page_type=page_type)

    def get_as_soup(self) -> BeautifulSoup:
        return BeautifulSoup(self.html, features="lxml")
