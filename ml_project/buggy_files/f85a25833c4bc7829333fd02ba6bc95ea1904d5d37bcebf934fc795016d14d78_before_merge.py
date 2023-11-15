def fold_arguments(pysig, args, kws, normal_handler, default_handler,
                   stararg_handler):
    """
    Given the signature *pysig*, explicit *args* and *kws*, resolve
    omitted arguments and keyword arguments. A tuple of positional
    arguments is returned.
    Various handlers allow to process arguments:
    - normal_handler(index, param, value) is called for normal arguments
    - default_handler(index, param, default) is called for omitted arguments
    - stararg_handler(index, param, values) is called for a "*args" argument
    """

    # deal with kwonly args
    params = pysig.parameters
    kwonly = []
    for name, p in params.items():
        if p.kind == p.KEYWORD_ONLY:
            kwonly.append(name)

    if kwonly:
        bind_args = args[:-len(kwonly)]
    else:
        bind_args = args
    bind_kws = kws.copy()
    if kwonly:
        for idx, n in enumerate(kwonly):
            bind_kws[n] = args[len(kwonly) + idx]

    # now bind
    ba = pysig.bind(*bind_args, **bind_kws)
    for i, param in enumerate(pysig.parameters.values()):
        name = param.name
        default = param.default
        if param.kind == param.VAR_POSITIONAL:
            # stararg may be omitted, in which case its "default" value
            # is simply the empty tuple
            ba.arguments[name] = stararg_handler(i, param,
                                                 ba.arguments.get(name, ()))
        elif name in ba.arguments:
            # Non-stararg, present
            ba.arguments[name] = normal_handler(i, param, ba.arguments[name])
        else:
            # Non-stararg, omitted
            assert default is not param.empty
            ba.arguments[name] = default_handler(i, param, default)
    # Collect args in the right order
    args = tuple(ba.arguments[param.name]
                 for param in pysig.parameters.values())
    return args