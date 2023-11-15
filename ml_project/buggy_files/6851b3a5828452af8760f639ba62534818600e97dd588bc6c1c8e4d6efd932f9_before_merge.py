    def all(self, axis=0, bool_only=None, skipna=True, level=None, **kwargs):
        """Return whether all elements are True over requested axis

        Note:
            If axis=None or axis=0, this call applies df.all(axis=1)
                to the transpose of df.
        """
        if axis is not None:
            axis = self._get_axis_number(axis)
            if bool_only and axis == 0:
                if hasattr(self, "dtype"):
                    raise NotImplementedError(
                        "{}.{} does not implement numeric_only.".format(
                            self.__name__, "all"
                        )
                    )
                data_for_compute = self[self.columns[self.dtypes == np.bool]]
                return data_for_compute.all(
                    axis=axis, bool_only=False, skipna=skipna, level=level, **kwargs
                )
            if level is not None:
                if bool_only is not None:
                    raise NotImplementedError(
                        "Option bool_only is not implemented with option level."
                    )
                return self._handle_level_agg(
                    axis, level, "all", skipna=skipna, **kwargs
                )
            return self._reduce_dimension(
                self._query_compiler.all(
                    axis=axis, bool_only=bool_only, skipna=skipna, level=level, **kwargs
                )
            )
        else:
            if bool_only:
                raise ValueError("Axis must be 0 or 1 (got {})".format(axis))
            # Reduce to a scalar if axis is None.
            if level is not None:
                return self._handle_level_agg(
                    axis, level, "all", skipna=skipna, **kwargs
                )
            else:
                result = self._reduce_dimension(
                    self._query_compiler.all(
                        axis=0,
                        bool_only=bool_only,
                        skipna=skipna,
                        level=level,
                        **kwargs,
                    )
                )
            if isinstance(result, BasePandasDataset):
                return result.all(
                    axis=axis, bool_only=bool_only, skipna=skipna, level=level, **kwargs
                )
            return result