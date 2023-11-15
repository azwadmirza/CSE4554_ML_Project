    def _wrap_applied_output(self, keys, values, not_indexed_same=False):
        if len(keys) == 0:
            return self.obj._constructor(index=keys)

        # GH12824
        first_not_none = next(com.not_none(*values), None)

        if first_not_none is None:
            # GH9684 - All values are None, return an empty frame.
            return self.obj._constructor()
        elif isinstance(first_not_none, DataFrame):
            return self._concat_objects(keys, values, not_indexed_same=not_indexed_same)

        key_index = self.grouper.result_index if self.as_index else None

        if isinstance(first_not_none, (np.ndarray, Index)):
            # GH#1738: values is list of arrays of unequal lengths
            #  fall through to the outer else clause
            # TODO: sure this is right?  we used to do this
            #  after raising AttributeError above
            return self.obj._constructor_sliced(
                values, index=key_index, name=self._selection_name
            )
        elif not isinstance(first_not_none, Series):
            # values are not series or array-like but scalars
            # self._selection_name not passed through to Series as the
            # result should not take the name of original selection
            # of columns
            if self.as_index:
                return self.obj._constructor_sliced(values, index=key_index)
            else:
                result = DataFrame(values, index=key_index, columns=[self._selection])
                self._insert_inaxis_grouper_inplace(result)
                return result
        else:
            # values are Series
            return self._wrap_applied_output_series(
                keys, values, not_indexed_same, first_not_none, key_index
            )