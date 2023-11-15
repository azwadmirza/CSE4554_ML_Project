def _period_array_cmp(cls, op):
    """
    Wrap comparison operations to convert Period-like to PeriodDtype
    """
    opname = '__{name}__'.format(name=op.__name__)
    nat_result = True if opname == '__ne__' else False

    def wrapper(self, other):
        op = getattr(self.asi8, opname)
        # We want to eventually defer to the Series or PeriodIndex (which will
        # return here with an unboxed PeriodArray). But before we do that,
        # we do a bit of validation on type (Period) and freq, so that our
        # error messages are sensible
        not_implemented = isinstance(other, (ABCSeries, ABCIndexClass))
        if not_implemented:
            other = other._values

        if isinstance(other, Period):
            self._check_compatible_with(other)

            result = op(other.ordinal)
        elif isinstance(other, cls):
            self._check_compatible_with(other)

            if not_implemented:
                return NotImplemented
            result = op(other.asi8)

            mask = self._isnan | other._isnan
            if mask.any():
                result[mask] = nat_result

            return result
        elif other is NaT:
            result = np.empty(len(self.asi8), dtype=bool)
            result.fill(nat_result)
        else:
            other = Period(other, freq=self.freq)
            result = op(other.ordinal)

        if self._hasnans:
            result[self._isnan] = nat_result

        return result

    return compat.set_function_name(wrapper, opname, cls)