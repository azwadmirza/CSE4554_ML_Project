    def __get__(self, instance, owner):
        if self._handle is None:
            self._handle = self.factory(instance)
        return self._handle