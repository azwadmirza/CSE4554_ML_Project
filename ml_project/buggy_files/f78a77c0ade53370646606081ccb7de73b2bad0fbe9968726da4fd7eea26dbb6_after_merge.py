    def take(self, indices, allow_fill=False, fill_value=None):
        if (allow_fill is False or (allow_fill and fill_value is self.dtype.na_value)) \
                and len(self) > 0:
            return type(self)(self[indices], dtype=self._dtype)

        if self._use_arrow:
            array = self._arrow_array.to_pandas().to_numpy()
        else:
            array = self._ndarray

        replace = False
        if allow_fill and \
                (fill_value is None or fill_value == self._dtype.na_value):
            fill_value = self.dtype.na_value
            replace = True

        result = take(array, indices, fill_value=fill_value,
                      allow_fill=allow_fill)
        del array
        if replace and pa is not None:
            # pyarrow cannot recognize pa.NULL
            result[result == self.dtype.na_value] = None
        return type(self)(result, dtype=self._dtype)