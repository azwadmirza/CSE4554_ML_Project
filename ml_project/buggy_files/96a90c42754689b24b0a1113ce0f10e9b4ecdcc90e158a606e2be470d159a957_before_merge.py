    def _try_cast(arr, take_fast_path):

        # perf shortcut as this is the most common case
        if take_fast_path:
            if _possibly_castable(arr) and not copy and dtype is None:
                return arr

        try:
            subarr = _possibly_cast_to_datetime(arr, dtype)
            if not is_internal_type(subarr):
                subarr = np.array(subarr, dtype=dtype, copy=copy)
        except (ValueError, TypeError):
            if is_categorical_dtype(dtype):
                subarr = Categorical(arr)
            elif dtype is not None and raise_cast_failure:
                raise
            else:
                subarr = np.array(arr, dtype=object, copy=copy)
        return subarr