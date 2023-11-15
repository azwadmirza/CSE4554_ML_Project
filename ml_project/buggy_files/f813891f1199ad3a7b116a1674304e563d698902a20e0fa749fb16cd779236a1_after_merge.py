def proxy(opts, functions=None, returners=None, whitelist=None, utils=None):
    '''
    Returns the proxy module for this salt-proxy-minion
    '''
    ret = LazyLoader(
        _module_dirs(opts, 'proxy', 'proxy'),
        opts,
        tag='proxy',
        pack={'__salt__': functions, '__ret__': returners, '__utils__': utils},
    )

    ret.pack['__proxy__'] = ret

    return ret