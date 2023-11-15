    def _compute_map_reduce_metadata(self, axis, new_parts):
        if axis == 0:
            columns = self.columns
            index = ["__reduced__"]
            new_lengths = [1]
            new_widths = self._column_widths
            new_dtypes = self._dtypes
        else:
            columns = ["__reduced__"]
            index = self.index
            new_lengths = self._row_lengths
            new_widths = [1]
            if self._dtypes is not None:
                new_dtypes = pandas.Series(
                    np.full(1, find_common_type(self.dtypes.values)),
                    index=["__reduced__"],
                )
            else:
                new_dtypes = self._dtypes
        return self.__constructor__(
            new_parts,
            index,
            columns,
            new_lengths,
            new_widths,
            new_dtypes,
            validate_axes="reduced",
        )