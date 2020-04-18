from pystock.attributes.attribute import PageContent


class MetaPage(type):
    """
    値のget, setに関するメタクラス
    """
    def __new__(meta, name, bases, class_dict):
        for key, value in class_dict.items():
            if isinstance(value, PageContent):
                value.name = key
                value.internal_name = '_' + key
        cls = type.__new__(meta, name, bases, class_dict)
        return cls


class AbstractPage(object, metaclass=MetaPage):
    pass


class Page(AbstractPage):
    pass
