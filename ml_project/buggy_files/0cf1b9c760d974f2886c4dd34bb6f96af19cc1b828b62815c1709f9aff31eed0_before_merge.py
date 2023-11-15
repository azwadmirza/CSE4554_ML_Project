    def __call__(self, x1, x2):
        if isinstance(x1, SERIES_TYPE) and isinstance(x2, DATAFRAME_TYPE):
            # reject invokeing series's op on dataframe
            raise NotImplementedError
        return self._call(x1, x2)