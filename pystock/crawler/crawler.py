from pystock.attributes.attribute import Field
from pystock.crawler.user_agent import UserAgent
from pystock.errors import CrawlPageNotFoundError
from datetime import datetime, timedelta, timezone
import requests


class MetaCrawler(type):
    """
    値のget, setに関するメタクラス
    """
    def __new__(meta, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, Field):
                value.name = key
                value.internal_name = '_' + key
        cls = type.__new__(meta, name, bases, class_dict)
        return cls


class AbstractCrawler(object, metaclass=MetaCrawler):
    pass


class Crawler(AbstractCrawler):

    def __init__(self):
        """
        インスタンスを生成
        """
        pass

    def __call__(self, **kwargs) -> dict:
        url = None
        text = None
        if "url" in kwargs:
            url = kwargs['url']
            text = self.get_url_text(target_url=url)
            url = None
        if "text" in kwargs:
            text = kwargs['text']
        # 両方に値が含まれている場合は例外を投げる
        if (url is not None) and (text is not None):
            raise ValueError("両方に値を設定しないでください")
        result = self.web_scraping(text)
        return result

    def web_scraping(self, text: str) -> dict:
        """
        textより情報を抽出する
        :params text: webページ
        """
        raise NotImplementedError("please implement your code")

    def get_url_text(self, target_url: str) -> str:
        """
        requestsを使って、webからページを取得し、htmlを返す
        """
        user_agent = UserAgent.get_user_agent_header()
        r = requests.get(
            target_url,
            headers=user_agent)

        if r.status_code != 200:
            raise CrawlPageNotFoundError(url=target_url)

        # 日本語に対応
        r.encoding = r.apparent_encoding
        return r.text

    @staticmethod
    def get_crawl_datetime() -> str:
        jst = timezone(timedelta(hours=+9), 'JST')
        now = datetime.now(jst)
        return now.strftime("%Y-%m-%dT%H:%M:%S")
