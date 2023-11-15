    def from_scalars(cls, values):
        if pa is None or cls._pandas_only():
            return cls._from_sequence(values)
        else:
            arrow_array = pa.chunked_array([cls._to_arrow_array(values)])
            return cls(arrow_array)