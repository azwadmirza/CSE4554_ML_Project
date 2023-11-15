def kernel_mode(func):
    """
    A decorator for kernel functions.

    When eager mode is on, expressions will be executed after `new_entities`, however
    `new_entities` is also called in `Executor` and `OperandTilesHandler`, this decorator
    provides an options context for kernel functions to avoid execution.
    """

    def _wrapped(*args, **kwargs):
        _kernel_mode.eager = False
        return_value = func(*args, **kwargs)
        _kernel_mode.eager = None
        return return_value

    return _wrapped