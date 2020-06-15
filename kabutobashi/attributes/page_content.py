from kabutobashi.errors import TagNotFoundError


class PageContent(object):
    """
    WebPageからCrawlしてきた値を保持するクラス。
    値を入力する際に改行や空白などの文字を自動で削除する
    """
    def __init__(
            self,
            tag1: str = None,
            _class1: str = None,
            _id1: str = None,
            tag2: str = None,
            _class2: str = None,
            _id2: str = None,
            required=False,
            alternative_data=None,
            required_type=None,
            value_candidate=None):
        """
        :params required: True if value is required
        :params required_type: specify type if the type is fixed
        :params value_candidte: list the candidate values
        :params find_all: find()ではなく、find_all()でデータを取得する
        """
        self.name = None
        self.internal_name = None
        # tagを取得する方法
        self.tag1 = tag1
        self._class1 = {"class": _class1}
        self._id1 = {"id": _id1}
        self.tag2 = tag2
        self._class2 = {"class": _class2}
        self._id2 = {"id": _id2}
        # 値を設定する際の条件など
        self.required: bool = required
        self.alternative_data = alternative_data
        self.required_type: type = required_type
        self.value_candidate: list = value_candidate

    def __get__(self, instance, instance_type):
        return getattr(instance, self.internal_name, None)

    def __set__(self, instance, value):
        if value is None:
            raise ValueError(f"The field is required and none is invalid")

        set_value = None
        # tag1から取得
        if self.tag1 is not None:
            if self._class1['class'] is not None:
                set_value = value.find(self.tag1, self._class1)
            else:
                set_value = value.find(self.tag1)

        # 値がない場合はerror
        if set_value is None and self.required:
            raise TagNotFoundError(tag=self.tag1)

        # tag2もある場合は、追加で取得
        if self.tag2 is not None:
            if self._class2['class'] is not None:
                set_value = set_value.find(self.tag2, self._class2)
            else:
                set_value = set_value.find(self.tag2)

        # 値がない場合はerror
        if set_value is None and self.required:
            raise TagNotFoundError(tag=self.tag2)

        # 文字列を置換して保持
        if set_value is not None:
            set_value = self.replace(set_value.get_text())
        else:
            set_value = self.alternative_data
        setattr(instance, self.internal_name, set_value)

    @staticmethod
    def replace(input_text: str) -> str:
        return input_text.replace(" ", "") \
            .replace("\t", "").replace("\n", "").replace("\r", "") \
            .replace("\xa0", " ").replace("円", "")
