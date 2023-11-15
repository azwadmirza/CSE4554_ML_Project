    def __init__(self, key: str, value: str, reason: Any = None, object: bytes = None):
        message = ("invalid value {value!r} ({type}) for key {key!r}{reason}"
                   "".format(value=value, type=type(value), key=key,
                             reason=': ' + reason if reason else ''))
        self.object = object
        super().__init__(message)