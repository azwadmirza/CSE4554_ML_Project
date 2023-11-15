    def call_cython(arg, window, minp):
        minp = _use_window(minp, window)
        return _tseries.roll_generic(arg, window, minp, func)