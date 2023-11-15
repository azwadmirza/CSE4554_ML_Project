    def read(self, size=-1):
        if size == -1:
            return self._body.read()
        return self._body.read(size)