    def _set_result_index_ordered(
        self, result: "OutputFrameOrSeries"
    ) -> "OutputFrameOrSeries":
        # set the result index on the passed values object and
        # return the new object, xref 8046

        if self.grouper.is_monotonic:
            # shortcut if we have an already ordered grouper
            result.set_axis(self.obj._get_axis(self.axis), axis=self.axis, inplace=True)
            return result

        # row order is scrambled => sort the rows by position in original index
        original_positions = Index(
            np.concatenate(self._get_indices(self.grouper.result_index))
        )
        result.set_axis(original_positions, axis=self.axis, inplace=True)
        result = result.sort_index(axis=self.axis)

        dropped_rows = len(result.index) < len(self.obj.index)

        if dropped_rows:
            # get index by slicing original index according to original positions
            # slice drops attrs => use set_axis when no rows were dropped
            sorted_indexer = result.index
            result.index = self._selected_obj.index[sorted_indexer]
        else:
            result.set_axis(self.obj._get_axis(self.axis), axis=self.axis, inplace=True)

        return result