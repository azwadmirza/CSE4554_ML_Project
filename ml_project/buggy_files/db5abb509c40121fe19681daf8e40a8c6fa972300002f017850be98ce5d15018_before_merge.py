    def f(arg, window, min_periods=None, time_rule=None):
        def call_cython(arg, window, minp):
            minp = check_minp(minp, window)
            return func(arg, window, minp)
        return _rolling_moment(arg, window, call_cython, min_periods,
                               time_rule=time_rule)