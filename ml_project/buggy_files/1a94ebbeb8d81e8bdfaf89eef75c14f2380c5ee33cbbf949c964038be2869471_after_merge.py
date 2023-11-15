    def astype(self, dtype, copy=True):
        dtype = pandas_dtype(dtype)
        if isinstance(dtype, ArrowStringDtype):
            if copy:
                return self.copy()
            return self

        if pa is None or self._force_use_pandas:
            # pyarrow not installed
            if isinstance(dtype, ArrowDtype):
                dtype = dtype.type
            return type(self)(pd.Series(self.to_numpy()).astype(dtype, copy=copy))

        # try to slice 1 record to get the result dtype
        test_array = self._arrow_array.slice(0, 1).to_pandas()
        test_result_array = test_array.astype(dtype).array

        result_array = \
            type(test_result_array)(
                np.full(self.shape, test_result_array.dtype.na_value,
                        dtype=np.asarray(test_result_array).dtype))

        start = 0
        # use chunks to do astype
        for chunk_array in self._arrow_array.chunks:
            result_array[start: start + len(chunk_array)] = \
                chunk_array.to_pandas().astype(dtype).array
            start += len(chunk_array)
        return result_array