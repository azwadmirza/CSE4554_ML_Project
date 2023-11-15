    def astype(self, dtype, copy=True):
        msg = f'cannot astype from {self.dtype} to {dtype}'
        dtype = pandas_dtype(dtype)
        if isinstance(dtype, ArrowListDtype):
            if self.dtype == dtype:
                if copy:
                    return self.copy()
                return self
            else:
                if self._use_arrow:
                    try:
                        arrow_array = self._arrow_array.cast(dtype.arrow_type)
                        return ArrowListArray(arrow_array)
                    except (NotImplementedError, pa.ArrowInvalid):
                        raise TypeError(msg)
                else:
                    def f(x):
                        return pd.Series(x).astype(dtype.type).tolist()

                    try:
                        arr = pd.Series(self._ndarray)
                        ret = arr.map(f).to_numpy()
                        return ArrowStringArray(ret)
                    except ValueError:
                        raise TypeError(msg)

        try:
            return super().astype(dtype, copy=copy)
        except ValueError:
            raise TypeError(msg)