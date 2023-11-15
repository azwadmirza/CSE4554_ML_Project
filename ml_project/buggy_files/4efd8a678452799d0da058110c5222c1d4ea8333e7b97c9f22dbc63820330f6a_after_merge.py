def _dt_index_cmp(opname, cls, nat_result=False):
    """
    Wrap comparison operations to convert datetime-like to datetime64
    """

    def wrapper(self, other):
        func = getattr(super(DatetimeIndex, self), opname)

        if isinstance(other, (datetime, compat.string_types)):
            if isinstance(other, datetime):
                # GH#18435 strings get a pass from tzawareness compat
                self._assert_tzawareness_compat(other)

            other = _to_m8(other, tz=self.tz)
            result = func(other)
            if isna(other):
                result.fill(nat_result)
        else:
            if isinstance(other, list):
                other = DatetimeIndex(other)
            elif not isinstance(other, (np.ndarray, Index, ABCSeries)):
                other = _ensure_datetime64(other)

            if is_datetimelike(other):
                self._assert_tzawareness_compat(other)

            result = func(np.asarray(other))
            result = _values_from_object(result)

            if isinstance(other, Index):
                o_mask = other.values.view('i8') == libts.iNaT
            else:
                o_mask = other.view('i8') == libts.iNaT

            if o_mask.any():
                result[o_mask] = nat_result

        if self.hasnans:
            result[self._isnan] = nat_result

        # support of bool dtype indexers
        if is_bool_dtype(result):
            return result
        return Index(result)

    return compat.set_function_name(wrapper, opname, cls)