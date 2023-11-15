def register_trainable(name, trainable):
    """Register a trainable function or class.

    Args:
        name (str): Name to register.
        trainable (obj): Function or tune.Trainable clsas. Functions must
            take (config, status_reporter) as arguments and will be
            automatically converted into a class during registration.
    """

    if isinstance(trainable, FunctionType):
        trainable = wrap_function(trainable)
    if not issubclass(trainable, Trainable):
        raise TypeError(
            "Second argument must be convertable to Trainable", trainable)
    _default_registry.register(TRAINABLE_CLASS, name, trainable)