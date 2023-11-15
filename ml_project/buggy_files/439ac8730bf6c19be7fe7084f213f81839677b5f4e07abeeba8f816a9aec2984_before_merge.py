    def sum(self, axis=0, *args, **kwargs):
        """
        Sum of non-NA/null values

        Returns
        -------
        sum : float
        """
        nv.validate_sum(args, kwargs)
        valid_vals = self._valid_sp_values
        sp_sum = valid_vals.sum()
        if self._null_fill_value:
            return sp_sum
        else:
            nsparse = self.sp_index.ngaps
            return sp_sum + self.fill_value * nsparse