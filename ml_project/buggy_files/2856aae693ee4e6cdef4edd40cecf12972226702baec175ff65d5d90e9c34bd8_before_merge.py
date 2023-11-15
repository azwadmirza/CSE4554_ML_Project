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