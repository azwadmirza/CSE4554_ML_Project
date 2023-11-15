def get_clouds():
    clouds = []
    config = get_config_parser()
    # Start off with known clouds and apply config file on top of current config
    for c in KNOWN_CLOUDS:
        _config_add_cloud(config, c)
    config.read(CLOUD_CONFIG_FILE)
    for section in config.sections():
        c = Cloud(section)
        for option in config.options(section):
            if option == 'profile':
                c.profile = config.get(section, option)
            if option.startswith('endpoint_'):
                setattr(c.endpoints, option.replace('endpoint_', ''), config.get(section, option))
            elif option.startswith('suffix_'):
                setattr(c.suffixes, option.replace('suffix_', ''), config.get(section, option))
        if c.profile is None:
            # If profile isn't set, use latest
            setattr(c, 'profile', 'latest')
        if c.profile not in API_PROFILES:
            raise CLIError('Profile {} does not exist or is not supported.'.format(c.profile))
        if not c.endpoints.has_endpoint_set('management') and \
                c.endpoints.has_endpoint_set('resource_manager'):
            # If management endpoint not set, use resource manager endpoint
            c.endpoints.management = c.endpoints.resource_manager
        clouds.append(c)
    active_cloud_name = get_active_cloud_name()
    for c in clouds:
        if c.name == active_cloud_name:
            c.is_active = True
            break
    return clouds