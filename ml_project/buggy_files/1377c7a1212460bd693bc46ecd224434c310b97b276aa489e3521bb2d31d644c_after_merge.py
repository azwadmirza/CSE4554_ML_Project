    def wrapper(self, other):
        func = getattr(super(DatetimeIndex, self), opname)
        if isinstance(other, datetime):
            func = getattr(self, opname)
            other = _to_m8(other)
        elif isinstance(other, list):
            other = DatetimeIndex(other)
        elif not isinstance(other, np.ndarray):
            other = _ensure_datetime64(other)
        result = func(other)

        try:
            return result.view(np.ndarray)
        except:
            return result