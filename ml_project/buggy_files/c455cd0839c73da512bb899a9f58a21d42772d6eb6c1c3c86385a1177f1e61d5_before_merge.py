    def update(self, iterable):
        self._members = self.union(iterable)._members