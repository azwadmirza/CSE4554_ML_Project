    def fillna(self, value=None, method=None, limit=None):
        cls = type(self)

        if pa is None or self._force_use_pandas:
            # pyarrow not installed
            return cls(pd.Series(self.to_numpy()).fillna(
                value=value, method=method, limit=limit))

        chunks = []
        for chunk_array in self._arrow_array.chunks:
            array = chunk_array.to_pandas()
            if method is None:
                result_array = self._array_fillna(array, value)
            else:
                result_array = array.fillna(value=value, method=method,
                                            limit=limit)
            chunks.append(pa.array(result_array, from_pandas=True))
        return cls(pa.chunked_array(chunks), dtype=self._dtype)