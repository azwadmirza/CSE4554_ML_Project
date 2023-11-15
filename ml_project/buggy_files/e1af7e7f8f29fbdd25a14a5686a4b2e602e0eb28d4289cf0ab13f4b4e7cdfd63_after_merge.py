    def __getattr__(self, k):
        if hasattr(self.__dict__, k):
            r = getattr(self.__dict__, k)
        else:
            if self.__dict__.get('_path', None) is not None:
                r = getattr(self._path, k)
            else:
                raise AttributeError(k)
        if isinstance(r, pathlib.Path):
            return Path(r)
        return r