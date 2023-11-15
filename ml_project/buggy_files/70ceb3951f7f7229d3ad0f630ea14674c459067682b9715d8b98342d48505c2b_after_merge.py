    def _from_sequence(cls, scalars, dtype=None, copy=False):
        if pa is None or cls._pandas_only():
            # pyarrow not installed, just return numpy
            ret = np.empty(len(scalars), dtype=object)
            ret[:] = scalars
            return cls(ret)

        if pa_null is not None and isinstance(scalars, type(pa_null)):
            scalars = []
        elif not hasattr(scalars, 'dtype'):
            ret = np.empty(len(scalars), dtype=object)
            for i, s in enumerate(scalars):
                ret[i] = s
            scalars = ret
        elif isinstance(scalars, cls):
            if copy:
                scalars = scalars.copy()
            return scalars
        arrow_array = pa.chunked_array([cls._to_arrow_array(scalars)])
        return cls(arrow_array, dtype=dtype, copy=copy)