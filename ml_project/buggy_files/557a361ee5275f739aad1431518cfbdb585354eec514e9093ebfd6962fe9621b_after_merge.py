    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # add events for each field
        self._events.source = self
        self._events.add(**dict.fromkeys(self.__fields__))