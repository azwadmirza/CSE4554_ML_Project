    def __init__(
        self,
        isolation_level=None,
        json_serializer=None,
        json_deserializer=None,
        **kwargs
    ):
        default.DefaultDialect.__init__(self, **kwargs)
        self.isolation_level = isolation_level
        self._json_deserializer = json_deserializer
        self._json_serializer = json_serializer