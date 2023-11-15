def get_argnames(func):
    """Introspecs the arguments of a callable.

    Args:
        func: The callable to introspect

    Returns:
        A list of argument names, excluding *arg and **kwargs
        arguments.
    """

    if six.PY2:
        func_object = _get_func_if_nested(func)
        spec = _get_argspec(func_object)

        args = spec.args

    else:
        sig = inspect.signature(func)

        args = [
            param.name
            for param in sig.parameters.values()
            if param.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]

    # NOTE(kgriffs): Depending on the version of Python, 'self' may or may not
    # be present, so we normalize the results by removing 'self' as needed.
    # Note that this behavior varies between 3.x versions as well as between
    # 3.x and 2.7.
    if args[0] == 'self':
        args = args[1:]

    return args