    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add events for each field
        self._events.source = self
        self._events.add(**dict.fromkeys(self.__fields__))