    def __init__(self, pyfunc, otypes='', doc=None, excluded=None,
                 cache=False):
        self.pyfunc = pyfunc
        self.cache = cache

        if doc is None:
            self.__doc__ = pyfunc.__doc__
        else:
            self.__doc__ = doc

        if isinstance(otypes, str):
            self.otypes = otypes
            for char in self.otypes:
                if char not in typecodes['All']:
                    raise ValueError(
                        "Invalid otype specified: %s" % (char,))
        elif iterable(otypes):
            self.otypes = ''.join([_nx.dtype(x).char for x in otypes])
        else:
            raise ValueError(
                "Invalid otype specification")

        # Excluded variable support
        if excluded is None:
            excluded = set()
        self.excluded = set(excluded)

        if self.otypes and not self.excluded:
            self._ufunc = None      # Caching to improve default performance