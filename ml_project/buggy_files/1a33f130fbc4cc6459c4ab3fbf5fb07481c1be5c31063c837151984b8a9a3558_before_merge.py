    def astype(self, dtype, copy=True):
        msg = f'cannot astype from {self.dtype} to {dtype}'
        dtype = pandas_dtype(dtype)
        if isinstance(dtype, ArrowListDtype):
            if self.dtype == dtype:
                if copy:
                    return self.copy()
                return self
            else:
                try:
                    arrow_array = self._arrow_array.cast(dtype.arrow_type)
                    return ArrowListArray(arrow_array)
                except (NotImplementedError, pa.ArrowInvalid):
                    raise TypeError(msg)

        try:
            return super().astype(dtype, copy=copy)
        except ValueError:
            raise TypeError(msg)