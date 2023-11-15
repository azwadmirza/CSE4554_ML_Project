    def _bottleneck_reduce(cls, func):
        """
        Methods to return a wrapped function for any function `func` for
        bottoleneck method, except for `median`.
        """

        def wrapped_func(self, **kwargs):
            from .dataarray import DataArray

            # bottleneck doesn't allow min_count to be 0, although it should
            # work the same as if min_count = 1
            if self.min_periods is not None and self.min_periods == 0:
                min_count = 1
            else:
                min_count = self.min_periods

            axis = self.obj.get_axis_num(self.dim)

            padded = self.obj.variable
            if self.center:
                if (LooseVersion(np.__version__) < LooseVersion('1.13') and
                        self.obj.dtype.kind == 'b'):
                    # with numpy < 1.13 bottleneck cannot handle np.nan-Boolean
                    # mixed array correctly. We cast boolean array to float.
                    padded = padded.astype(float)

                if isinstance(padded.data, dask_array_type):
                    # Workaround to make the padded chunk size is larger than
                    # self.window-1
                    shift = - (self.window - 1)
                    offset = -shift - self.window // 2
                    valid = (slice(None), ) * axis + (
                        slice(offset, offset + self.obj.shape[axis]), )
                else:
                    shift = (-self.window // 2) + 1
                    valid = (slice(None), ) * axis + (slice(-shift, None), )
                padded = padded.pad_with_fill_value(**{self.dim: (0, -shift)})

            if isinstance(padded.data, dask_array_type):
                values = dask_rolling_wrapper(func, padded,
                                              window=self.window,
                                              min_count=min_count,
                                              axis=axis)
            else:
                values = func(padded.data, window=self.window,
                              min_count=min_count, axis=axis)

            if self.center:
                values = values[valid]
            result = DataArray(values, self.obj.coords)

            return result
        return wrapped_func