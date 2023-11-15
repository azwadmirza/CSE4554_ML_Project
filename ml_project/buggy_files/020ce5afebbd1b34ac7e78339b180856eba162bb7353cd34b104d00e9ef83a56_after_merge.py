def beacons(opts, functions, context=None, proxy=None):
    '''
    Load the beacon modules

    :param dict opts: The Salt options dictionary
    :param dict functions: A dictionary of minion modules, with module names as
                            keys and funcs as values.
    '''
    return LazyLoader(
        _module_dirs(opts, 'beacons'),
        opts,
        tag='beacons',
        virtual_funcs=['__validate__'],
        pack={'__context__': context, '__salt__': functions, '__proxy__': proxy or {}},
    )