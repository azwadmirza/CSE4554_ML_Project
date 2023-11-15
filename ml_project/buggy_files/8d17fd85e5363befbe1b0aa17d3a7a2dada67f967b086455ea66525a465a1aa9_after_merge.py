def grains(opts, force_refresh=False, proxy=None):
    '''
    Return the functions for the dynamic grains and the values for the static
    grains.

    .. code-block:: python

        import salt.config
        import salt.loader

        __opts__ = salt.config.minion_config('/etc/salt/minion')
        __grains__ = salt.loader.grains(__opts__)
        print __grains__['id']
    '''
    # if we hae no grains, lets try loading from disk (TODO: move to decorator?)
    cfn = os.path.join(
        opts['cachedir'],
        'grains.cache.p'
    )
    if not force_refresh:
        if opts.get('grains_cache', False):
            if os.path.isfile(cfn):
                grains_cache_age = int(time.time() - os.path.getmtime(cfn))
                if opts.get('grains_cache_expiration', 300) >= grains_cache_age and not \
                        opts.get('refresh_grains_cache', False) and not force_refresh:
                    log.debug('Retrieving grains from cache')
                    try:
                        serial = salt.payload.Serial(opts)
                        with salt.utils.fopen(cfn, 'rb') as fp_:
                            cached_grains = serial.load(fp_)
                        return cached_grains
                    except (IOError, OSError):
                        pass
                else:
                    if force_refresh:
                        log.debug('Grains refresh requested. Refreshing grains.')
                    else:
                        log.debug('Grains cache last modified {0} seconds ago and '
                                  'cache expiration is set to {1}. '
                                  'Grains cache expired. Refreshing.'.format(
                                      grains_cache_age,
                                      opts.get('grains_cache_expiration', 300)
                                  ))
            else:
                log.debug('Grains cache file does not exist.')

    if opts.get('skip_grains', False):
        return {}
    if 'conf_file' in opts:
        pre_opts = {}
        pre_opts.update(salt.config.load_config(
            opts['conf_file'], 'SALT_MINION_CONFIG',
            salt.config.DEFAULT_MINION_OPTS['conf_file']
        ))
        default_include = pre_opts.get(
            'default_include', opts['default_include']
        )
        include = pre_opts.get('include', [])
        pre_opts.update(salt.config.include_config(
            default_include, opts['conf_file'], verbose=False
        ))
        pre_opts.update(salt.config.include_config(
            include, opts['conf_file'], verbose=True
        ))
        if 'grains' in pre_opts:
            opts['grains'] = pre_opts['grains']
        else:
            opts['grains'] = {}
    else:
        opts['grains'] = {}

    grains_data = {}
    funcs = grain_funcs(opts)
    if force_refresh:  # if we refresh, lets reload grain modules
        funcs.clear()
    # Run core grains
    for key, fun in six.iteritems(funcs):
        if not key.startswith('core.'):
            continue
        log.trace('Loading {0} grain'.format(key))
        ret = fun()
        if not isinstance(ret, dict):
            continue
        grains_data.update(ret)

    # Run the rest of the grains
    for key, fun in six.iteritems(funcs):
        if key.startswith('core.') or key == '_errors':
            continue
        try:
            ret = fun()
        except Exception:
            log.critical(
                'Failed to load grains defined in grain file {0} in '
                'function {1}, error:\n'.format(
                    key, fun
                ),
                exc_info=True
            )
            continue
        if not isinstance(ret, dict):
            continue
        grains_data.update(ret)

    grains_data.update(opts['grains'])
    # Write cache if enabled
    if opts.get('grains_cache', False):
        cumask = os.umask(0o77)
        try:
            if salt.utils.is_windows():
                # Make sure cache file isn't read-only
                __salt__['cmd.run']('attrib -R "{0}"'.format(cfn))
            with salt.utils.fopen(cfn, 'w+b') as fp_:
                try:
                    serial = salt.payload.Serial(opts)
                    serial.dump(grains_data, fp_)
                except TypeError:
                    # Can't serialize pydsl
                    pass
        except (IOError, OSError):
            msg = 'Unable to write to grains cache file {0}'
            log.error(msg.format(cfn))
        os.umask(cumask)

    return grains_data