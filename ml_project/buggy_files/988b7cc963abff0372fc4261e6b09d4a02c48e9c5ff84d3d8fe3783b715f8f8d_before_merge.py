    def _get_max_shape(self, shape, max_shape):
        if max_shape is None:
            return tuple([s or self._int32max for s in shape])
        elif isinstance(max_shape, int):
            assert max_shape == shape[0]
            return self._get_max_shape(shape, None)
        else:
            max_shape = tuple(max_shape)
            assert len(shape) == len(max_shape)
            for (s, ms) in zip(shape, max_shape):
                assert s == ms or s is None and isinstance(ms, int)
            return max_shape