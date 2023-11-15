def validate_service_names(config):
    for service_name in config.keys():
        if not isinstance(service_name, six.string_types):
            raise ConfigurationError(
                "Service name: {} needs to be a string, eg '{}'".format(
                    service_name,
                    service_name))