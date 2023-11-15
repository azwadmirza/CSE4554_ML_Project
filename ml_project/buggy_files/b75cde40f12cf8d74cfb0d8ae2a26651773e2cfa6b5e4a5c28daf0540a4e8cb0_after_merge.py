def _rolling_func(func, desc, check_minp=_use_window):
    @Substitution(desc, _unary_arg, _type_of_input)
    @Appender(_doc_template)
    @wraps(func)
    def f(arg, window, min_periods=None, freq=None, time_rule=None):
        def call_cython(arg, window, minp):
            minp = check_minp(minp, window)
            return func(arg, window, minp)
        return _rolling_moment(arg, window, call_cython, min_periods,
                               freq=freq, time_rule=time_rule)

    return f