def format_environment(environment):
    def format_env(key, value):
        if value is None:
            return key
        if isinstance(value, six.binary_type):
            value = value.decode('utf-8')
        return '{key}={value}'.format(key=key, value=value)
    return [format_env(*item) for item in environment.items()]