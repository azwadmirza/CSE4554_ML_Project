def beacons(opts, functions, context=None):
    '''
    Load the beacon modules

    :param dict opts: The Salt options dictionary
    :param dict functions: A dictionary of minion modules, with module names as
                            keys and funcs as values.
    '''
    if context is None:
        context = {}
    return LazyLoader(_module_dirs(opts, 'beacons', 'beacons'),
                      opts,
                      tag='beacons',
                      pack={'__context__': context,
                            '__salt__': functions})