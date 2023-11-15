    def wrapper(self, other, axis=None):
        # Validate the axis parameter
        if axis is not None:
            self._get_axis_number(axis)

        if isinstance(other, ABCSeries):
            name = _maybe_match_name(self, other)
            if len(self) != len(other):
                raise ValueError('Series lengths must match to compare')
            return self._constructor(na_op(self.values, other.values),
                                     index=self.index, name=name)
        elif isinstance(other, pd.DataFrame):  # pragma: no cover
            return NotImplemented
        elif isinstance(other, (np.ndarray, pd.Index)):
            if len(self) != len(other):
                raise ValueError('Lengths must match to compare')
            return self._constructor(na_op(self.values, np.asarray(other)),
                                     index=self.index).__finalize__(self)
        elif isinstance(other, pd.Categorical):
            if not is_categorical_dtype(self):
                msg = ("Cannot compare a Categorical for op {op} with Series "
                       "of dtype {typ}.\nIf you want to compare values, use "
                       "'series <op> np.asarray(other)'.")
                raise TypeError(msg.format(op=op, typ=self.dtype))

        if is_categorical_dtype(self):
            # cats are a special case as get_values() would return an ndarray,
            # which would then not take categories ordering into account
            # we can go directly to op, as the na_op would just test again and
            # dispatch to it.
            res = op(self.values, other)
        else:
            values = self.get_values()
            if isinstance(other, (list, np.ndarray)):
                other = np.asarray(other)

            res = na_op(values, other)
            if isscalar(res):
                raise TypeError('Could not compare %s type with Series' %
                                type(other))

            # always return a full value series here
            res = _values_from_object(res)

        res = pd.Series(res, index=self.index, name=self.name, dtype='bool')
        return res