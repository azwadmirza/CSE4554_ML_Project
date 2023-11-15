    def f(arg, window, min_periods=None, freq=None, time_rule=None, **kwargs):
        def call_cython(arg, window, minp, **kwds):
            minp = check_minp(minp, window)
            return func(arg, window, minp, **kwds)
        return _rolling_moment(arg, window, call_cython, min_periods,
                               freq=freq, time_rule=time_rule, **kwargs)