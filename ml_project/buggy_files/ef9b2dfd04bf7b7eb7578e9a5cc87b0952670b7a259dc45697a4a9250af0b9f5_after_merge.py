    def __eq__(self, other):
        if isinstance(other, (str, bytes)):
            other = self.__class__(other)
        return (
            self.__class__ == other.__class__
            and self._base_parts == other._base_parts
            and self._path == other._path
            and self._extra_parts == other._extra_parts
        )