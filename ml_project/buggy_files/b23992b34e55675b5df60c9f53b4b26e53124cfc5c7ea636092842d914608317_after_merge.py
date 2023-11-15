    def check_value_shape(self, value, slice_):
        """Checks if value can be set to the slice"""
        if None not in self.shape and self.dtype != "O":
            if not all([isinstance(sh, int) for sh in slice_]):
                expected_value_shape = tuple(
                    [
                        len(range(*slice_shape.indices(self.shape[i])))
                        for i, slice_shape in enumerate(slice_)
                        if not isinstance(slice_shape, int)
                    ]
                )

                if isinstance(value, list):
                    value = np.array(value)
                if isinstance(value, np.ndarray):
                    value_shape = [dim for dim in value.shape if dim != 1]
                    expected_shape = [dim for dim in expected_value_shape if dim != 1]
                    if value_shape != expected_shape:
                        raise ValueShapeError(expected_value_shape, value.shape)
                    else:
                        value = value.reshape(expected_value_shape)
            else:
                expected_value_shape = (1,)
                if isinstance(value, list):
                    value = np.array(value)
                if (
                    isinstance(value, np.ndarray)
                    and value.shape != expected_value_shape
                ):
                    raise ValueShapeError(expected_value_shape, value.shape)
        return value