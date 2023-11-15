def _td_array_cmp(cls, op):
    """
    Wrap comparison operations to convert timedelta-like to timedelta64
    """
    opname = '__{name}__'.format(name=op.__name__)
    nat_result = True if opname == '__ne__' else False

    meth = getattr(dtl.DatetimeLikeArrayMixin, opname)

    def wrapper(self, other):
        if _is_convertible_to_td(other) or other is NaT:
            try:
                other = _to_m8(other)
            except ValueError:
                # failed to parse as timedelta
                return ops.invalid_comparison(self, other, op)

            result = meth(self, other)
            if isna(other):
                result.fill(nat_result)

        elif not is_list_like(other):
            return ops.invalid_comparison(self, other, op)

        elif len(other) != len(self):
            raise ValueError("Lengths must match")

        else:
            try:
                other = type(self)._from_sequence(other)._data
            except (ValueError, TypeError):
                return ops.invalid_comparison(self, other, op)

            result = meth(self, other)
            result = com.values_from_object(result)

            o_mask = np.array(isna(other))
            if o_mask.any():
                result[o_mask] = nat_result

        if self._hasnans:
            result[self._isnan] = nat_result

        return result

    return compat.set_function_name(wrapper, opname, cls)