    def _simple_new(cls, values, name=None, dtype=None):
        """
        We require that we have a dtype compat for the values. If we are passed
        a non-dtype compat, then coerce using the constructor.

        Must be careful not to recurse.
        """
        if isinstance(values, (ABCSeries, ABCIndexClass)):
            # Index._data must always be an ndarray.
            # This is no-copy for when _values is an ndarray,
            # which should be always at this point.
            values = np.asarray(values._values)

        result = object.__new__(cls)
        result._data = values
        # _index_data is a (temporary?) fix to ensure that the direct data
        # manipulation we do in `_libs/reduction.pyx` continues to work.
        # We need access to the actual ndarray, since we're messing with
        # data buffers and strides. We don't re-use `_ndarray_values`, since
        # we actually set this value too.
        result._index_data = values
        result._name = name

        return result._reset_identity()