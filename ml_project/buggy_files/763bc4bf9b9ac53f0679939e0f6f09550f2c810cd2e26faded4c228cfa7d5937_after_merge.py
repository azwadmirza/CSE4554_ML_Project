    def __get__(self, instance, owner):
        instance.setup()
        if self._handle is None:
            self._handle = self.factory(instance)
        return self._handle