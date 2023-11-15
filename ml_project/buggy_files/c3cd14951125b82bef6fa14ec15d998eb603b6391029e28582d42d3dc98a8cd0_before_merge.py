    def __call__(self, series, dtype):
        if dtype is None:
            inferred_dtype = None
            if callable(self._arg):
                # arg is a function, try to inspect the signature
                sig = inspect.signature(self._arg)
                return_type = sig.return_annotation
                if return_type is not inspect._empty:
                    inferred_dtype = np.dtype(return_type)
            else:
                if isinstance(self._arg, MutableMapping):
                    inferred_dtype = pd.Series(self._arg).dtype
                else:
                    inferred_dtype = self._arg.dtype
            if inferred_dtype is not None and np.issubdtype(inferred_dtype, np.number):
                if np.issubdtype(inferred_dtype, np.inexact):
                    # for the inexact e.g. float
                    # we can make the decision,
                    # but for int, due to the nan which may occur,
                    # we cannot infer the dtype
                    dtype = inferred_dtype
            else:
                dtype = inferred_dtype

        if dtype is None:
            raise ValueError('cannot infer dtype, '
                             'it needs to be specified manually for `map`')
        else:
            dtype = np.int64 if dtype is int else dtype
            dtype = np.dtype(dtype)

        inputs = [series]
        if isinstance(self._arg, SERIES_TYPE):
            inputs.append(self._arg)
        return self.new_series(inputs, shape=series.shape, dtype=dtype,
                               index_value=series.index_value, name=series.name)