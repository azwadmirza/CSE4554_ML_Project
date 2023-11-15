    def __lt__(self, a):
        if isinstance(a, visidata.Path):
            return self._path.__lt__(a._path)
        return self._path.__lt__(a)