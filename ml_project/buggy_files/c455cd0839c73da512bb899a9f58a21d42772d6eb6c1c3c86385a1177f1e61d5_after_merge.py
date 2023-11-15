    def update(self, iterable):
        self._members.update((id(obj), obj) for obj in iterable)