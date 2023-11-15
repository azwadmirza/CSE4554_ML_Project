def _validate_minkowski_kwargs(X, m, n, **kwargs):
    if 'w' in kwargs:
        kwargs['w'] = _convert_to_double(kwargs['w'])
    if 'p' not in kwargs:
        kwargs['p'] = 2.
    return kwargs