    def get_reindexed_values(self, empty_dtype, upcasted_na):

        if upcasted_na is None:
            # No upcasting is necessary
            fill_value = self.block.fill_value
            values = self.block.get_values()
        else:
            fill_value = upcasted_na

            if self.is_null:
                if getattr(self.block, 'is_object', False):
                    # we want to avoid filling with np.nan if we are
                    # using None; we already know that we are all
                    # nulls
                    values = self.block.values.ravel(order='K')
                    if len(values) and values[0] is None:
                        fill_value = None

                if getattr(self.block, 'is_datetimetz', False):
                    pass
                elif getattr(self.block, 'is_categorical', False):
                    pass
                else:
                    missing_arr = np.empty(self.shape, dtype=empty_dtype)
                    missing_arr.fill(fill_value)
                    return missing_arr

            if not self.indexers:
                if not self.block._can_consolidate:
                    # preserve these for validation in _concat_compat
                    return self.block.values

            if self.block.is_bool:
                # External code requested filling/upcasting, bool values must
                # be upcasted to object to avoid being upcasted to numeric.
                values = self.block.astype(np.object_).values
            else:
                # No dtype upcasting is done here, it will be performed during
                # concatenation itself.
                values = self.block.get_values()

        if not self.indexers:
            # If there's no indexing to be done, we want to signal outside
            # code that this array must be copied explicitly.  This is done
            # by returning a view and checking `retval.base`.
            values = values.view()

        else:
            for ax, indexer in self.indexers.items():
                values = algos.take_nd(values, indexer, axis=ax,
                                       fill_value=fill_value)

        return values