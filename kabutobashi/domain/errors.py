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


class TagNotFoundError(KabutobashiPageError):
    """
    crawlしたいページに対象のtagがない場合に返すエラー
    """

    def __init__(self, tag):
        super().__init__(url="")
        self.tag = tag

    def __str__(self):
        return f"tag [{self.tag}] not found"


class KabutobashiMethodError(KabutobashiBaseError):
    pass


class KabutobashiVisualizeError(KabutobashiBaseError):
    pass


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


class KabutobashiBlockDecoratorError(KabutobashiBaseError):
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
