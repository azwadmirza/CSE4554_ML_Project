def minion_config(path,
                  env_var='SALT_MINION_CONFIG',
                  defaults=None,
                  check_dns=None):
    '''
    Reads in the minion configuration file and sets up special options
    '''
    if check_dns is not None:
        # All use of the `check_dns` arg was removed in `598d715`. The keyword
        # argument was then removed in `9d893e4` and `**kwargs` was then added
        # in `5d60f77` in order not to break backwards compatibility.
        #
        # Showing a deprecation for 0.17.0 and 0.18.0 should be enough for any
        # api calls to be updated in order to stop it's use.
        salt.utils.warn_until(
            (0, 19),
            'The functionality behind the \'check_dns\' keyword argument is '
            'no longer required, as such, it became unnecessary and is now '
            'deprecated. \'check_dns\' will be removed in salt > 0.18.0'
        )
    if defaults is None:
        defaults = DEFAULT_MINION_OPTS

    overrides = load_config(path, env_var, DEFAULT_MINION_OPTS['conf_file'])
    default_include = overrides.get('default_include',
                                    defaults['default_include'])
    include = overrides.get('include', [])

    overrides.update(include_config(default_include, path, verbose=False))
    overrides.update(include_config(include, path, verbose=True))

    opts = apply_minion_config(overrides, defaults)
    _validate_opts(opts)
    return opts