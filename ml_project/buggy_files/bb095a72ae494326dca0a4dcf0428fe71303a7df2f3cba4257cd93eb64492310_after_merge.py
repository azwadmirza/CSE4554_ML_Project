    def is_null(self):
        if self.block is None:
            return True

        if not self.block._can_hold_na:
            return False

        # Usually it's enough to check but a small fraction of values to see if
        # a block is NOT null, chunks should help in such cases.  1000 value
        # was chosen rather arbitrarily.
        values = self.block.values
        if self.block.is_categorical:
            values_flat = values.categories
        elif self.block.is_sparse:
            # fill_value is not NaN and have holes
            if not values._null_fill_value and values.sp_index.ngaps > 0:
                return False
            values_flat = values.ravel(order='K')
        else:
            values_flat = values.ravel(order='K')
        total_len = values_flat.shape[0]
        chunk_len = max(total_len // 40, 1000)
        for i in range(0, total_len, chunk_len):
            if not isnull(values_flat[i:i + chunk_len]).all():
                return False

        return True