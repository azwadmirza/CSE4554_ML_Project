    def __init__(self, values, dtype: ArrowListDtype=None, copy=False):
        if dtype is None:
            if isinstance(values, type(self)):
                dtype = values.dtype
            elif pa is not None:
                if isinstance(values, pa.Array):
                    dtype = ArrowListDtype(values.type.value_type)
                elif isinstance(values, pa.ChunkedArray):
                    dtype = ArrowListDtype(values.type.value_type)
                else:
                    values = pa.array(values)
                    if values.type == pa.null():
                        dtype = ArrowListDtype(pa.string())
                    else:
                        dtype = ArrowListDtype(values.type.value_type)
            else:
                value_type = np.asarray(values[0]).dtype
                dtype = ArrowListDtype(value_type)

        super().__init__(values, dtype=dtype, copy=copy)