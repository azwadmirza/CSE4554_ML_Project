def load_config(filename='mkdocs.yml', options=None):
    user_config = options or {}
    if 'config' in user_config:
        filename = user_config.pop('config')
    if not os.path.exists(filename):
        raise ConfigurationError("Config file '%s' does not exist." % filename)
    with open(filename, 'r') as fp:
        local_config = yaml.load(fp)
    if local_config:
        user_config.update(local_config)
    return validate_config(user_config)