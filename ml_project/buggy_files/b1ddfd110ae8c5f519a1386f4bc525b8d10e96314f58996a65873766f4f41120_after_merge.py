def inject_bottleneck_rolling_methods(cls):
    # standard numpy reduce methods
    methods = [(name, globals()[name]) for name in NAN_REDUCE_METHODS]
    for name, f in methods:
        func = cls._reduce_method(f)
        func.__name__ = name
        func.__doc__ = _ROLLING_REDUCE_DOCSTRING_TEMPLATE.format(
            name=func.__name__, da_or_ds='DataArray')
        setattr(cls, name, func)

    # bottleneck rolling methods
    if has_bottleneck:
        # TODO: Bump the required version of bottlneck to 1.1 and remove all
        # these version checks (see GH#1278)
        bn_version = LooseVersion(bn.__version__)
        bn_min_version = LooseVersion('1.0')
        bn_version_1_1 = LooseVersion('1.1')
        if bn_version < bn_min_version:
            return

        for bn_name, method_name in BOTTLENECK_ROLLING_METHODS.items():
            try:
                f = getattr(bn, bn_name)
                func = cls._bottleneck_reduce(f)
                func.__name__ = method_name
                func.__doc__ = _ROLLING_REDUCE_DOCSTRING_TEMPLATE.format(
                    name=func.__name__, da_or_ds='DataArray')
                setattr(cls, method_name, func)
            except AttributeError as e:
                # skip functions not in Bottleneck 1.0
                if ((bn_version < bn_version_1_1) and
                        (bn_name not in ['move_var', 'move_argmin',
                                         'move_argmax', 'move_rank'])):
                    raise e

        # bottleneck rolling methods without min_count (bn.__version__ < 1.1)
        f = getattr(bn, 'move_median')
        if bn_version >= bn_version_1_1:
            func = cls._bottleneck_reduce(f)
        else:
            func = cls._bottleneck_reduce_without_min_count(f)
        func.__name__ = 'median'
        func.__doc__ = _ROLLING_REDUCE_DOCSTRING_TEMPLATE.format(
            name=func.__name__, da_or_ds='DataArray')
        setattr(cls, 'median', func)