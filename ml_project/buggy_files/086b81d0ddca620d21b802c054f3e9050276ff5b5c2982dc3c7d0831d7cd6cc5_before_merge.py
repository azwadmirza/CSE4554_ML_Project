def master_config(path, env_var='SALT_MASTER_CONFIG', defaults=None):
    '''
    Reads in the master configuration file and sets up default options
    '''
    if defaults is None:
        defaults = DEFAULT_MASTER_OPTS

    overrides = load_config(path, env_var)
    default_include = overrides.get('default_include',
                                    defaults['default_include'])
    include = overrides.get('include', [])

    overrides.update(include_config(default_include, path, verbose=False))
    overrides.update(include_config(include, path, verbose=True))
    opts = apply_master_config(overrides, defaults)
    _validate_opts(opts)
    return opts