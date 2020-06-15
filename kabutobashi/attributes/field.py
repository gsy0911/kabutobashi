class Field(object):
    """
    様々な値の保持に用いるクラス。
    値を代入する際にバリデーションが行われる。
    """
    def __init__(
            self,
            required=False,
            required_type=None,
            value_candidate=None):
        """
        :params required: True if value is required
        :params required_type: specify type if the type is fixed
        :params value_candidte: list the candidate values
        """
        self.name = None
        self.internal_name = None
        self.required: bool = required
        self.required_type: type = required_type
        self.value_candidate: list = value_candidate

    def __get__(self, instance, instance_type):
        return getattr(instance, self.internal_name, None)

    def __set__(self, instance, value):
        if value is None:
            if self.required:
                raise ValueError(f"The field is required and none is invalid")
            else:
                return

        if self.required_type is not None:
            if type(value) is not self.required_type:
                raise TypeError(f"{self.required_type} is required, but {type(value)}(:={value}) is given")
        if self.value_candidate is not None:
            if value not in self.value_candidate:
                raise ValueError(f"{value} is not accepted, candidates are [{','.join(self.value_candidate)}]")
        setattr(instance, self.internal_name, value)
