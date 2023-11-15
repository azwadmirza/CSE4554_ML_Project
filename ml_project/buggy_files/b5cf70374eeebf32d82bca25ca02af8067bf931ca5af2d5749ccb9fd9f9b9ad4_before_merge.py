    def reset(self, *args) -> Timer:
        self.__init__(self._average)
        return self