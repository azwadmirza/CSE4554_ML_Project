    def _try_coerce_args(self, values, other):
        """ localize and return i8 for the values """
        values = values.tz_localize(None).asi8

        if is_null_datelike_scalar(other):
            other = tslib.iNaT
        elif isinstance(other, self._holder):
            if other.tz != self.values.tz:
                raise ValueError("incompatible or non tz-aware value")
            other = other.tz_localize(None).asi8
        elif isinstance(other, (np.datetime64, datetime)):
            other = lib.Timestamp(other)
            if not getattr(other, 'tz', None):
                raise ValueError("incompatible or non tz-aware value")
            other = other.value

        return values, other