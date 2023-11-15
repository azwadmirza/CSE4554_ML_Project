    def collapsed(self, dims_to_collapse=None):
        """
        Returns a copy of this coordinate, which has been collapsed along
        the specified dimensions.

        Replaces the points & bounds with a simple bounded region.
        """
        import dask.array as da
        # Ensure dims_to_collapse is a tuple to be able to pass
        # through to numpy
        if isinstance(dims_to_collapse, (int, np.integer)):
            dims_to_collapse = (dims_to_collapse, )
        if isinstance(dims_to_collapse, list):
            dims_to_collapse = tuple(dims_to_collapse)

        if np.issubdtype(self.dtype, np.str_):
            # Collapse the coordinate by serializing the points and
            # bounds as strings.
            def serialize(x):
                return '|'.join([str(i) for i in x.flatten()])
            bounds = None
            string_type_fmt = 'S{}' if six.PY2 else 'U{}'
            if self.has_bounds():
                shape = self._bounds_dm.shape[1:]
                bounds = []
                for index in np.ndindex(shape):
                    index_slice = (slice(None),) + tuple(index)
                    bounds.append(serialize(self.bounds[index_slice]))
                dtype = np.dtype(string_type_fmt.format(max(map(len, bounds))))
                bounds = np.array(bounds, dtype=dtype).reshape((1,) + shape)
            points = serialize(self.points)
            dtype = np.dtype(string_type_fmt.format(len(points)))
            # Create the new collapsed coordinate.
            coord = self.copy(points=np.array(points, dtype=dtype),
                              bounds=bounds)
        else:
            # Collapse the coordinate by calculating the bounded extremes.
            if self.ndim > 1:
                msg = 'Collapsing a multi-dimensional coordinate. ' \
                    'Metadata may not be fully descriptive for {!r}.'
                warnings.warn(msg.format(self.name()))
            elif not self.is_contiguous():
                msg = 'Collapsing a non-contiguous coordinate. ' \
                    'Metadata may not be fully descriptive for {!r}.'
                warnings.warn(msg.format(self.name()))

            if self.has_bounds():
                item = self.core_bounds()
                if dims_to_collapse is not None:
                    # Express main dims_to_collapse as non-negative integers
                    # and add the last (bounds specific) dimension.
                    dims_to_collapse = tuple(
                        dim % self.ndim for dim in dims_to_collapse) + (-1,)
            else:
                item = self.core_points()

            # Determine the array library for stacking
            al = da if _lazy.is_lazy_data(item) else np

            # Calculate the bounds and points along the right dims
            bounds = al.stack([item.min(axis=dims_to_collapse),
                               item.max(axis=dims_to_collapse)], axis=-1)
            points = al.array(bounds.sum(axis=-1) * 0.5, dtype=self.dtype)

            # Create the new collapsed coordinate.
            coord = self.copy(points=points, bounds=bounds)
        return coord