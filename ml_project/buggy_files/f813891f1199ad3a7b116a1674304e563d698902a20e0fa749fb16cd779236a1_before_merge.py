def proxy(opts, functions=None, returners=None, whitelist=None):
    '''
    Returns the proxy module for this salt-proxy-minion
    '''
    ret = LazyLoader(
        _module_dirs(opts, 'proxy', 'proxy'),
        opts,
        tag='proxy',
        pack={'__salt__': functions, '__ret__': returners},
    )

    ret.pack['__proxy__'] = ret

    return ret