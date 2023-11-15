    def __eq__(self, other):
        if hasattr(other, '_song'):
            other = other._song
        return self._song == other