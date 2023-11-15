def ignores_kwargs(*kwarg_names):
    '''
    Decorator to filter out unexpected keyword arguments from the call

    kwarg_names:
        List of argument names to ignore
    '''
    def _ignores_kwargs(fn):
        def __ignores_kwargs(*args, **kwargs):
            kwargs_filtered = kwargs.copy()
            for name in kwarg_names:
                if name in kwargs_filtered:
                    del kwargs_filtered[name]
            return fn(*args, **kwargs_filtered)
        return __ignores_kwargs
    return _ignores_kwargs