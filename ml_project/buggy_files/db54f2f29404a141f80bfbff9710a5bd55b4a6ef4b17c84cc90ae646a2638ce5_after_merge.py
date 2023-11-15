def _validate_minkowski_kwargs(X, m, n, **kwargs):
    if 'p' not in kwargs:
        kwargs['p'] = 2.
    return kwargs