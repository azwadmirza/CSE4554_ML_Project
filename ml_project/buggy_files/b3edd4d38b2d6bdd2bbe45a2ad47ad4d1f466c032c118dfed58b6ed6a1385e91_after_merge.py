def ssh_wrapper(opts, functions=None, context=None):
    '''
    Returns the custom logging handler modules
    '''
    return LazyLoader(_module_dirs(opts,
                                   'wrapper',
                                   'wrapper',
                                   base_path=os.path.join(SALT_BASE_PATH, os.path.join('client', 'ssh'))),
                      opts,
                      tag='wrapper',
                      pack={'__salt__': functions, '__context__': context},
                      )