def utils(opts, whitelist=None, context=None):
    '''
    Returns the utility modules
    '''
    return LazyLoader(_module_dirs(opts, 'utils', 'utils', ext_type_dirs='utils_dirs'),
                      opts,
                      tag='utils',
                      whitelist=whitelist,
                      pack={'__context__': context})