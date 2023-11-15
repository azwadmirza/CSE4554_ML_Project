    def __new__(self):
        return self._data.view(self)