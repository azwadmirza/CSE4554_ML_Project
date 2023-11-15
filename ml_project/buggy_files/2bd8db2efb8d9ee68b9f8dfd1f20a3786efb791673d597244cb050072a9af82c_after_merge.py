    def take(self, indices, allow_fill=False, fill_value=None):
        if allow_fill is False or (allow_fill and fill_value is self.dtype.na_value):
            return type(self)(self[indices], dtype=self._dtype)

        array = self._arrow_array.to_pandas().to_numpy()

        replace = False
        if allow_fill and fill_value is None:
            fill_value = self.dtype.na_value
            replace = True

        result = take(array, indices, fill_value=fill_value,
                      allow_fill=allow_fill)
        del array
        if replace:
            # pyarrow cannot recognize pa.NULL
            result[result == self.dtype.na_value] = None
        return type(self)(result, dtype=self._dtype)