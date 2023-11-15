    def f(arg, window, min_periods=None, freq=None, center=False,
          **kwargs):
        def call_cython(arg, window, minp, args=(), kwargs={}, **kwds):
            minp = check_minp(minp, window)
            return func(arg, window, minp, **kwds)
        return _rolling_moment(arg, window, call_cython, min_periods, freq=freq,
                               center=center, **kwargs)