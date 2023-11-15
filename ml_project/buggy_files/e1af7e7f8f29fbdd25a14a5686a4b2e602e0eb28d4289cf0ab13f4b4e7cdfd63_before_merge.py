    def __getattr__(self, k):
        if hasattr(self.__dict__, k):
            r = getattr(self.__dict__, k)
        else:
            r = getattr(self._path, k)
        if isinstance(r, pathlib.Path):
            return Path(r)
        return r