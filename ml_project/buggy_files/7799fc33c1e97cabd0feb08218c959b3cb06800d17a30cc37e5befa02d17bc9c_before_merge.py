def load_config(filename='mkdocs.yml', options=None):
    options = options or {}
    if 'config' in options:
        filename = options['config']
    if not os.path.exists(filename):
        raise ConfigurationError("Config file '%s' does not exist." % filename)
    with open(filename, 'r') as fp:
        user_config = yaml.load(fp)
    user_config.update(options)
    return validate_config(user_config)