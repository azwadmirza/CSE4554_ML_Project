    def _try_cast(self, result, obj, numeric_only=False):
        """
        Try to cast the result to our obj original type,
        we may have roundtripped through object in the mean-time.

        If numeric_only is True, then only try to cast numerics
        and not datetimelikes.

        """
        if obj.ndim > 1:
            dtype = obj._values.dtype
        else:
            dtype = obj.dtype

        if not is_scalar(result):
            if is_extension_array_dtype(dtype):
                # The function can return something of any type, so check
                # if the type is compatible with the calling EA.
                try:
                    result = obj._values._from_sequence(result, dtype=dtype)
                except Exception:
                    # https://github.com/pandas-dev/pandas/issues/22850
                    # pandas has no control over what 3rd-party ExtensionArrays
                    # do in _values_from_sequence. We still want ops to work
                    # though, so we catch any regular Exception.
                    pass
            elif numeric_only and is_numeric_dtype(dtype) or not numeric_only:
                result = maybe_downcast_to_dtype(result, dtype)

        return result