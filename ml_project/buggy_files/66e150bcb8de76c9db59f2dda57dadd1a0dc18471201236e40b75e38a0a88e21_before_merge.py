    def _getitem_slice(self, key):
        # If there is no step, we can fasttrack the codepath to use existing logic from
        # head and tail, which is already pretty fast.
        if (
            key.step is None
            and (isinstance(key.start, int) or key.start is None)
            and (isinstance(key.stop, int) or key.stop is None)
        ):
            if key.start is None and key.stop is None:
                return self.copy()

            def compute_offset(value):
                return (
                    value - len(self)
                    if value > 0
                    else value
                    if value != 0
                    else len(self)
                )

            # Head is a negative number, Tail is a positive number
            if key.start is None:
                return self.head(compute_offset(key.stop))
            elif key.stop is None:
                return self.tail(compute_offset(-key.start))
            return self.head(compute_offset(key.stop)).tail(compute_offset(-key.start))
        # We convert to a RangeIndex because getitem_row_array is expecting a list
        # of indices, and RangeIndex will give us the exact indices of each boolean
        # requested.
        if isinstance(key.start, int) and isinstance(key.stop, int):
            key = pandas.RangeIndex(len(self.index))[key]
        else:
            # To handle this case correctly, we let pandas compute the indices by
            # creating a MultiIndex ("a", "b") such that "a" is the original index and
            # "b" is the Range of numeric indices for each. Then we apply the slice to
            # the original index (named "a"), then extract the index values (named "b")
            # and pass that along to be sliced in the actual data. This also serves as a
            # validation that the input slice is usable and correct.
            key = pandas.DataFrame(
                index=pandas.MultiIndex.from_arrays(
                    [self.index, pandas.RangeIndex(len(self.index))], names=["a", "b"]
                )
            )[key].index.get_level_values("b")
        return self.__constructor__(
            query_compiler=self._query_compiler.getitem_row_array(key)
        )