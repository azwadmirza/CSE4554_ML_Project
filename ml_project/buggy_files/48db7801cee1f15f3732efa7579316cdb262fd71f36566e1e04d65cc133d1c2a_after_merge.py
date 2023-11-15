def _comp_method_SERIES(cls, op, special):
    """
    Wrapper function for Series arithmetic operations, to avoid
    code duplication.
    """
    op_name = _get_op_name(op, special)
    masker = _gen_eval_kwargs(op_name).get('masker', False)

    def na_op(x, y):
        # TODO:
        # should have guarantess on what x, y can be type-wise
        # Extension Dtypes are not called here

        # Checking that cases that were once handled here are no longer
        # reachable.
        assert not (is_categorical_dtype(y) and not is_scalar(y))

        if is_object_dtype(x.dtype):
            result = _comp_method_OBJECT_ARRAY(op, x, y)

        elif is_datetimelike_v_numeric(x, y):
            return invalid_comparison(x, y, op)

        else:

            # we want to compare like types
            # we only want to convert to integer like if
            # we are not NotImplemented, otherwise
            # we would allow datetime64 (but viewed as i8) against
            # integer comparisons

            # we have a datetime/timedelta and may need to convert
            assert not needs_i8_conversion(x)
            mask = None
            if not is_scalar(y) and needs_i8_conversion(y):
                mask = isna(x) | isna(y)
                y = y.view('i8')
                x = x.view('i8')

            method = getattr(x, op_name, None)
            if method is not None:
                with np.errstate(all='ignore'):
                    result = method(y)
                if result is NotImplemented:
                    return invalid_comparison(x, y, op)
            else:
                result = op(x, y)

            if mask is not None and mask.any():
                result[mask] = masker

        return result

    def wrapper(self, other, axis=None):
        # Validate the axis parameter
        if axis is not None:
            self._get_axis_number(axis)

        res_name = get_op_result_name(self, other)

        if isinstance(other, list):
            # TODO: same for tuples?
            other = np.asarray(other)

        if isinstance(other, ABCDataFrame):  # pragma: no cover
            # Defer to DataFrame implementation; fail early
            return NotImplemented

        elif isinstance(other, ABCSeries) and not self._indexed_same(other):
            raise ValueError("Can only compare identically-labeled "
                             "Series objects")

        elif is_categorical_dtype(self):
            # Dispatch to Categorical implementation; pd.CategoricalIndex
            # behavior is non-canonical GH#19513
            res_values = dispatch_to_index_op(op, self, other, pd.Categorical)
            return self._constructor(res_values, index=self.index,
                                     name=res_name)

        elif is_datetime64_dtype(self) or is_datetime64tz_dtype(self):
            # Dispatch to DatetimeIndex to ensure identical
            # Series/Index behavior
            if (isinstance(other, datetime.date) and
                    not isinstance(other, datetime.datetime)):
                # https://github.com/pandas-dev/pandas/issues/21152
                # Compatibility for difference between Series comparison w/
                # datetime and date
                msg = (
                    "Comparing Series of datetimes with 'datetime.date'.  "
                    "Currently, the 'datetime.date' is coerced to a "
                    "datetime. In the future pandas will not coerce, "
                    "and {future}. "
                    "To retain the current behavior, "
                    "convert the 'datetime.date' to a datetime with "
                    "'pd.Timestamp'."
                )

                if op in {operator.lt, operator.le, operator.gt, operator.ge}:
                    future = "a TypeError will be raised"
                else:
                    future = (
                        "'the values will not compare equal to the "
                        "'datetime.date'"
                    )
                msg = '\n'.join(textwrap.wrap(msg.format(future=future)))
                warnings.warn(msg, FutureWarning, stacklevel=2)
                other = pd.Timestamp(other)

            res_values = dispatch_to_index_op(op, self, other,
                                              pd.DatetimeIndex)

            return self._constructor(res_values, index=self.index,
                                     name=res_name)

        elif is_timedelta64_dtype(self):
            res_values = dispatch_to_index_op(op, self, other,
                                              pd.TimedeltaIndex)
            return self._constructor(res_values, index=self.index,
                                     name=res_name)

        elif (is_extension_array_dtype(self) or
              (is_extension_array_dtype(other) and not is_scalar(other))):
            # Note: the `not is_scalar(other)` condition rules out
            # e.g. other == "category"
            return dispatch_to_extension_op(op, self, other)

        elif isinstance(other, ABCSeries):
            # By this point we have checked that self._indexed_same(other)
            res_values = na_op(self.values, other.values)
            # rename is needed in case res_name is None and res_values.name
            # is not.
            return self._constructor(res_values, index=self.index,
                                     name=res_name).rename(res_name)

        elif isinstance(other, (np.ndarray, pd.Index)):
            # do not check length of zerodim array
            # as it will broadcast
            if other.ndim != 0 and len(self) != len(other):
                raise ValueError('Lengths must match to compare')

            res_values = na_op(self.values, np.asarray(other))
            result = self._constructor(res_values, index=self.index)
            # rename is needed in case res_name is None and self.name
            # is not.
            return result.__finalize__(self).rename(res_name)

        elif is_scalar(other) and isna(other):
            # numpy does not like comparisons vs None
            if op is operator.ne:
                res_values = np.ones(len(self), dtype=bool)
            else:
                res_values = np.zeros(len(self), dtype=bool)
            return self._constructor(res_values, index=self.index,
                                     name=res_name, dtype='bool')

        else:
            values = self.get_values()

            with np.errstate(all='ignore'):
                res = na_op(values, other)
            if is_scalar(res):
                raise TypeError('Could not compare {typ} type with Series'
                                .format(typ=type(other)))

            # always return a full value series here
            res_values = com.values_from_object(res)
            return self._constructor(res_values, index=self.index,
                                     name=res_name, dtype='bool')

    wrapper.__name__ = op_name
    return wrapper