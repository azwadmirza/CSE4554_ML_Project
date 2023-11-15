    def create_from_value(value, index, dtype):
        # return a new empty value suitable for the dtype

        if is_datetimetz(dtype):
            subarr = DatetimeIndex([value] * len(index), dtype=dtype)
        else:
            if not isinstance(dtype, (np.dtype, type(np.dtype))):
                dtype = dtype.dtype
            subarr = np.empty(len(index), dtype=dtype)
            subarr.fill(value)

        return subarr