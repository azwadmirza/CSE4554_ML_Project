def validate_service_names(func):
    @wraps(func)
    def func_wrapper(config):
        for service_name in config.keys():
            if type(service_name) is int:
                raise ConfigurationError(
                    "Service name: {} needs to be a string, eg '{}'".format(service_name, service_name)
                )
        return func(config)
    return func_wrapper