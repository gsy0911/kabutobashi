from kabutobashi.attributes import PageContent


class MetaPage(type):
    """
    値のget, setに関するメタクラス
    """
    def __new__(mcs, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, PageContent):
                value.name = key
                value.internal_name = '_' + key
        cls = type.__new__(mcs, name, bases, class_dict)
        return cls


class AbstractPage(object, metaclass=MetaPage):
    pass


class Page(AbstractPage):
    pass
