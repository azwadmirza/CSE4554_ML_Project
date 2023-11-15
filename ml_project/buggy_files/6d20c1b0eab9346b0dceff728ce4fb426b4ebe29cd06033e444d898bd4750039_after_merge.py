    def call_cython(arg, window, minp):
        minp = _use_window(minp, window)
        return lib.roll_quantile(arg, window, minp, quantile)