from typing import List


class KabutobashiBaseError(Exception):
    pass


class KabutobashiPageError(KabutobashiBaseError):
    """
    Crawlが失敗したときに返すエラー
    """

    def __init__(self, url: str = ""):
        self.url = url

    def __str__(self):
        return f"error occurred when crawling [{self.url}]"


class KabutobashiEntityError(KabutobashiBaseError):
    pass


class KabutobashiBlockError(KabutobashiBaseError):
    pass


class KabutobashiBlockInstanceMismatchError(KabutobashiBlockError):
    pass


class KabutobashiBlockParamsIsNoneError(KabutobashiBlockError):
    pass


class KabutobashiBlockSeriesIsNoneError(KabutobashiBlockError):
    pass


class KabutobashiBlockSeriesDtIsMissingError(KabutobashiBlockError):
    def __init__(self, code: str, dt: List[str]):
        self.code = code
        self.dt = dt

    def __str__(self):
        return f"{self.dt} in {self.code} is missing"


class KabutobashiBlockGlueError(KabutobashiBlockError):
    """
    KabutobashiBlockGlueError is base error for `BlockGlue`.
    """

    pass


class KabutobashiBlockDecoratorError(KabutobashiBlockError):
    """
    KabutobashiBlockDecoratorError is base error for `@block` decorator.
    """

    pass


class KabutobashiBlockDecoratorNameError(KabutobashiBlockDecoratorError):
    """
    class must end with `Block`.
    """

    pass


class KabutobashiBlockDecoratorTypeError(KabutobashiBlockDecoratorError):
    """
    fist argument of @block() must be type
    """

    pass


class KabutobashiBlockDecoratorReturnError(KabutobashiBlockDecoratorError):
    """
    function-return-type is not matched.
    """

    pass


class KabutobashiBlockDecoratorNotImplementedError(KabutobashiBlockDecoratorError):
    """
    The function that was intended to be implemented has not been implemented.
    """

    pass
