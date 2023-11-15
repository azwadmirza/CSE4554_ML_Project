    def __setitem__(self, key, value):
        """__setitem__ is overloaded to access the underlying numpy values with
        orthogonal indexing.

        See __getitem__ for more details.
        """
        dims, index_tuple, new_order = self._broadcast_indexes(key)

        if not isinstance(value, Variable):
            value = as_compatible_data(value)
            if value.ndim > len(dims):
                raise ValueError(
                    'shape mismatch: value array of shape %s could not be'
                    'broadcast to indexing result with %s dimensions'
                    % (value.shape, len(dims)))
            if value.ndim == 0:
                value = Variable((), value)
            else:
                value = Variable(dims[-value.ndim:], value)
        # broadcast to become assignable
        value = value.set_dims(dims).data

        if new_order:
            value = duck_array_ops.asarray(value)
            value = value[(len(dims) - value.ndim) * (np.newaxis,) +
                          (Ellipsis,)]
            value = np.moveaxis(value, new_order, range(len(new_order)))

        self._indexable_data[index_tuple] = value