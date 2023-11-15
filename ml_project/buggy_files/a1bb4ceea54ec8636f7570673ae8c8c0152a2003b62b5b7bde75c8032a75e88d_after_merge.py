def _fetch_option(cfg, ret_config, virtualname, attr_name):
    """
    Fetch a given option value from the config.

    @see :func:`get_returner_options`
    """
    # c_cfg is a dictionary returned from config.option for
    # any options configured for this returner.
    if isinstance(cfg, dict):
        c_cfg = cfg
    else:
        c_cfg = cfg('{0}'.format(virtualname), {})

    default_cfg_key = '{0}.{1}'.format(virtualname, attr_name)
    if not ret_config:
        # Using the default configuration key
        if isinstance(cfg, dict):
            return c_cfg.get(default_cfg_key, cfg.get(attr_name))
        else:
            return c_cfg.get(attr_name, cfg(default_cfg_key))

    # Using ret_config to override the default configuration key
    ret_cfg = cfg('{0}.{1}'.format(ret_config, virtualname), {})

    override_default_cfg_key = '{0}.{1}.{2}'.format(
        ret_config,
        virtualname,
        attr_name,
    )
    override_cfg_default = cfg(override_default_cfg_key)

    # Look for the configuration item in the override location
    ret_override_cfg = ret_cfg.get(
        attr_name,
        override_cfg_default
    )
    if ret_override_cfg:
        return ret_override_cfg

    # if not configuration item found, fall back to the default location.
    return c_cfg.get(attr_name, cfg(default_cfg_key))