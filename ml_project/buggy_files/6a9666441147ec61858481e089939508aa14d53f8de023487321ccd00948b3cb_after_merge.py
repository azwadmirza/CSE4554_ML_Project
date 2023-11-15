def executors(opts, functions=None, context=None, proxy=None):
    '''
    Returns the executor modules
    '''
    return LazyLoader(
        _module_dirs(opts, 'executors', 'executor'),
        opts,
        tag='executor',
        pack={'__salt__': functions, '__context__': context or {}, '__proxy__': proxy or {}},
    )