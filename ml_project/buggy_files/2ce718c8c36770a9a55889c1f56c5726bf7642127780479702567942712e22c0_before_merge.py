def infer_params(cls: Type[T], constructor: Callable[..., T] = None) -> Dict[str, Any]:
    if cls == FromParams:
        return {}
    if constructor is None:
        constructor = cls.__init__

    signature = inspect.signature(constructor)
    parameters = dict(signature.parameters)

    has_kwargs = False
    for param in parameters.values():
        if param.kind == param.VAR_KEYWORD:
            has_kwargs = True

    if not has_kwargs:
        return parameters

    # "mro" is "method resolution order".  The first one is the current class, the next is the
    # first superclass, and so on.  We take the first superclass we find that inherits from
    # FromParams.
    super_class = None
    for super_class_candidate in cls.mro()[1:]:
        if issubclass(super_class_candidate, FromParams):
            super_class = super_class_candidate
            break
    if super_class:
        super_parameters = infer_params(super_class)
    else:
        super_parameters = {}

    return {**super_parameters, **parameters}  # Subclass parameters overwrite superclass ones