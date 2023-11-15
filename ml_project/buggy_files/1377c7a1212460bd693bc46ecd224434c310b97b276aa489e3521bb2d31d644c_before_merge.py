    def wrapper(self, other):
        if isinstance(other, datetime):
            func = getattr(self, opname)
            result = func(_to_m8(other))
        elif isinstance(other, np.ndarray):
            func = getattr(super(DatetimeIndex, self), opname)
            result = func(other)
        else:
            other = _ensure_datetime64(other)
            func = getattr(super(DatetimeIndex, self), opname)
            result = func(other)
        try:
            return result.view(np.ndarray)
        except:
            return result