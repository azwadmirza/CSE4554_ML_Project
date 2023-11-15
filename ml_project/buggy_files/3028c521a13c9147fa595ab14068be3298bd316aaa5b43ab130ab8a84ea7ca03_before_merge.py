def format_environment(environment):
    def format_env(key, value):
        if value is None:
            return key
        return '{key}={value}'.format(key=key, value=value)
    return [format_env(*item) for item in environment.items()]