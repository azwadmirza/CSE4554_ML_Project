    def rcall(self, x1, x2):
        x1 = self._process_input(x1)
        x2 = self._process_input(x2)
        if isinstance(x1, SERIES_TYPE) and isinstance(x2, DATAFRAME_TYPE):
            # reject invoking series's op on dataframe
            raise NotImplementedError
        return self._call(x2, x1)