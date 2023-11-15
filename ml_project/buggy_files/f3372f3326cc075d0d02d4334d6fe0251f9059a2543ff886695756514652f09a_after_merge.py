    def _count_level(self, level, axis=0, numeric_only=False):
        if numeric_only:
            frame = self._get_numeric_data()
        else:
            frame = self

        count_axis = frame._get_axis(axis)
        agg_axis = frame._get_agg_axis(axis)

        if not isinstance(count_axis, ABCMultiIndex):
            raise TypeError(
                f"Can only count levels on hierarchical {self._get_axis_name(axis)}."
            )

        # Mask NaNs: Mask rows or columns where the index level is NaN, and all
        # values in the DataFrame that are NaN
        if frame._is_mixed_type:
            # Since we have mixed types, calling notna(frame.values) might
            # upcast everything to object
            values_mask = notna(frame).values
        else:
            # But use the speedup when we have homogeneous dtypes
            values_mask = notna(frame.values)

        index_mask = notna(count_axis.get_level_values(level=level))
        if axis == 1:
            mask = index_mask & values_mask
        else:
            mask = index_mask.reshape(-1, 1) & values_mask

        if isinstance(level, str):
            level = count_axis._get_level_number(level)

        level_name = count_axis._names[level]
        level_index = count_axis.levels[level]._shallow_copy(name=level_name)
        level_codes = ensure_int64(count_axis.codes[level])
        counts = lib.count_level_2d(mask, level_codes, len(level_index), axis=axis)

        if axis == 1:
            result = DataFrame(counts, index=agg_axis, columns=level_index)
        else:
            result = DataFrame(counts, index=level_index, columns=agg_axis)

        return result