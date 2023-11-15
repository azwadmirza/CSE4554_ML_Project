    def from_scalars(cls, values):
        arrow_array = pa.chunked_array([cls._to_arrow_array(values)])
        return cls(arrow_array)