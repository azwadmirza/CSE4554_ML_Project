def _rolling_func(func, desc, check_minp=_use_window, how=None):
    if how is None:
        how_arg_str = 'None'
    else:
        how_arg_str = "'%s"%how

    @Substitution(desc, _unary_arg, _roll_kw%how_arg_str, _type_of_input_retval,
                  _roll_notes)
    @Appender(_doc_template)
    @wraps(func)
    def f(arg, window, min_periods=None, freq=None, center=False, how=how,
          **kwargs):
        def call_cython(arg, window, minp, args=(), kwargs={}, **kwds):
            minp = check_minp(minp, window)
            return func(arg, window, minp, **kwds)
        return _rolling_moment(arg, window, call_cython, min_periods, freq=freq,
                               center=center, how=how, **kwargs)

    return f