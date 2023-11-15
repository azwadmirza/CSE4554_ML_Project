    def fillna(self, value=None, method=None, limit=None):
        chunks = []
        for chunk_array in self._arrow_array.chunks:
            array = chunk_array.to_pandas()
            if method is None:
                result_array = self._array_fillna(array, value)
            else:
                result_array = array.fillna(value=value, method=method,
                                            limit=limit)
            chunks.append(pa.array(result_array, from_pandas=True))
        return type(self)(pa.chunked_array(chunks), dtype=self._dtype)