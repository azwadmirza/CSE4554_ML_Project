def returners(opts, functions, whitelist=None, context=None):
    '''
    Returns the returner modules
    '''
    return LazyLoader(_module_dirs(opts, 'returners', 'returner'),
                      opts,
                      tag='returner',
                      whitelist=whitelist,
                      pack={'__salt__': functions,
                            '__context__': context})