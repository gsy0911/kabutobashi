

class PyStockBaseError(Exception):
    pass


class PyStockCrawlerError(PyStockBaseError):
    """
    Crawlが失敗したときに返すエラー
    """

    def __init__(self, url: str = ""):
        self.url = url

    def __str__(self):
        return f"error occurred when crawling [{self.url}]"


class CrawlPageNotFoundError(PyStockCrawlerError):
    """
    crawlしたいページがない場合に返すエラー
    """

    def __init__(self, url: str = ""):
        super().__init__(url=url)

    def __str__(self):
        return f"Page not found [{self.url}]"


class TagNotFoundError(PyStockCrawlerError):
    """
    crawlしたいページに対象のtagがない場合に返すエラー
    """

    def __init__(self, tag):
        super().__init__(url="")
        self.tag = tag

    def __str__(self):
        return f"tag [{self.tag}] not found"


class StockDfError(PyStockBaseError):
    pass


class PyStockMethodError(PyStockBaseError):
    pass


class PyStockVisualizeError(PyStockBaseError):
    pass


class PyStockAttributeError(PyStockBaseError):
    pass
