def states(opts, functions, utils, serializers, whitelist=None, proxy=None):
    '''
    Returns the state modules

    :param dict opts: The Salt options dictionary
    :param dict functions: A dictionary of minion modules, with module names as
                            keys and funcs as values.

    .. code-block:: python

        import salt.config
        import salt.loader

        __opts__ = salt.config.minion_config('/etc/salt/minion')
        statemods = salt.loader.states(__opts__, None, None)
    '''
    ret = LazyLoader(
        _module_dirs(opts, 'states', 'states'),
        opts,
        tag='states',
        pack={'__salt__': functions, '__proxy__': proxy or {}},
        whitelist=whitelist,
    )
    ret.pack['__states__'] = ret
    ret.pack['__utils__'] = utils
    ret.pack['__serializers__'] = serializers
    return ret