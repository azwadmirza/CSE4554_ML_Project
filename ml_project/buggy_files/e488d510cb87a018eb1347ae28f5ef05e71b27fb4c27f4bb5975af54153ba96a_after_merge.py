def func_parameters(func, *a, **kw):
    bowels = inspect.getargspec(func) if sys.version_info.major < 3 else inspect.getfullargspec(func)
    args_dict = dict(zip(bowels.args, map(represent,  a)))
    kwargs_dict = dict(zip(kw, list(map(lambda i: represent(kw[i]), kw))))
    kwarg_defaults = dict(zip(reversed(bowels.args), reversed(list(map(represent, bowels.defaults or ())))))
    kwarg_defaults.update(kwargs_dict)
    return args_dict, kwarg_defaults