    def __init__(self, value: Union[None, List[str], str] = None):
        if isinstance(value, str):
            value = StrConvert().to(value, of_type=List[str])
        self.all: bool = value is None or "ALL" in value
        self._names = value