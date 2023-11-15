    def _binop(self, other, func, level=None, fill_value=None):
        """
        Perform generic binary operation with optional fill value.

        Parameters
        ----------
        other : Series
        func : binary operator
        fill_value : float or object
            Value to substitute for NA/null values. If both Series are NA in a
            location, the result will be NA regardless of the passed fill value
        level : int or level name, default None
            Broadcast across a level, matching Index values on the
            passed MultiIndex level

        Returns
        -------
        Series
        """

        if not isinstance(other, Series):
            raise AssertionError('Other operand must be Series')

        new_index = self.index
        this = self

        if not self.index.equals(other.index):
            this, other = self.align(other, level=level, join='outer',
                                     copy=False)
            new_index = this.index

        this_vals, other_vals = ops.fill_binop(this.values, other.values,
                                               fill_value)

        with np.errstate(all='ignore'):
            result = func(this_vals, other_vals)

        name = ops.get_op_result_name(self, other)
        if func.__name__ in ['divmod', 'rdivmod']:
            ret = ops._construct_divmod_result(self, result, new_index, name)
        else:
            ret = ops._construct_result(self, result, new_index, name)
        return ret