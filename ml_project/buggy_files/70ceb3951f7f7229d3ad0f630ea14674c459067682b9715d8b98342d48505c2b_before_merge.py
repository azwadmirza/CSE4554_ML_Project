    def _from_sequence(cls, scalars, dtype=None, copy=False):
        if not hasattr(scalars, 'dtype'):
            ret = np.empty(len(scalars), dtype=object)
            for i, s in enumerate(scalars):
                ret[i] = s
            scalars = ret
        if isinstance(scalars, cls):
            if copy:
                scalars = scalars.copy()
            return scalars
        arrow_array = pa.chunked_array([cls._to_arrow_array(scalars)])
        return cls(arrow_array, dtype=dtype, copy=copy)