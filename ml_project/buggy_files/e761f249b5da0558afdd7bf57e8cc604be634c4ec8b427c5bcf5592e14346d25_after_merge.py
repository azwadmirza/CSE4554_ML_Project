def set_cloud_subscription(cloud_name, subscription):
    if not _get_cloud(cloud_name):
        raise CloudNotRegisteredException(cloud_name)
    config = get_config_parser()
    config.read(CLOUD_CONFIG_FILE)
    if subscription:
        try:
            config.add_section(cloud_name)
        except configparser.DuplicateSectionError:
            pass
        config.set(cloud_name, 'subscription', subscription)
    else:
        try:
            config.remove_option(cloud_name, 'subscription')
        except configparser.NoSectionError:
            pass
    if not os.path.isdir(GLOBAL_CONFIG_DIR):
        os.makedirs(GLOBAL_CONFIG_DIR)
    with open(CLOUD_CONFIG_FILE, 'w') as configfile:
        config.write(configfile)