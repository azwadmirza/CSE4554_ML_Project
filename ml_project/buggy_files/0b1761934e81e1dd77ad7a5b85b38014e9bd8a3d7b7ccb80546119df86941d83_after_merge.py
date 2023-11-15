def _dt_array_cmp(cls, op):
    """
    Wrap comparison operations to convert datetime-like to datetime64
    """
    opname = '__{name}__'.format(name=op.__name__)
    nat_result = True if opname == '__ne__' else False

    def wrapper(self, other):
        meth = getattr(dtl.DatetimeLikeArrayMixin, opname)

        other = lib.item_from_zerodim(other)

        if isinstance(other, (datetime, np.datetime64, compat.string_types)):
            if isinstance(other, (datetime, np.datetime64)):
                # GH#18435 strings get a pass from tzawareness compat
                self._assert_tzawareness_compat(other)

            try:
                other = _to_m8(other, tz=self.tz)
            except ValueError:
                # string that cannot be parsed to Timestamp
                return ops.invalid_comparison(self, other, op)

            result = op(self.asi8, other.view('i8'))
            if isna(other):
                result.fill(nat_result)
        elif lib.is_scalar(other) or np.ndim(other) == 0:
            return ops.invalid_comparison(self, other, op)
        elif len(other) != len(self):
            raise ValueError("Lengths must match")
        else:
            if isinstance(other, list):
                try:
                    other = type(self)._from_sequence(other)
                except ValueError:
                    other = np.array(other, dtype=np.object_)
            elif not isinstance(other, (np.ndarray, ABCIndexClass, ABCSeries,
                                        DatetimeArrayMixin)):
                # Following Timestamp convention, __eq__ is all-False
                # and __ne__ is all True, others raise TypeError.
                return ops.invalid_comparison(self, other, op)

            if is_object_dtype(other):
                result = op(self.astype('O'), np.array(other))
                o_mask = isna(other)
            elif not (is_datetime64_dtype(other) or
                      is_datetime64tz_dtype(other)):
                # e.g. is_timedelta64_dtype(other)
                return ops.invalid_comparison(self, other, op)
            else:
                self._assert_tzawareness_compat(other)
                if not hasattr(other, 'asi8'):
                    # ndarray, Series
                    other = type(self)(other)
                result = meth(self, other)
                o_mask = other._isnan

            result = com.values_from_object(result)

            # Make sure to pass an array to result[...]; indexing with
            # Series breaks with older version of numpy
            o_mask = np.array(o_mask)
            if o_mask.any():
                result[o_mask] = nat_result

        if self._hasnans:
            result[self._isnan] = nat_result

        return result

    return compat.set_function_name(wrapper, opname, cls)