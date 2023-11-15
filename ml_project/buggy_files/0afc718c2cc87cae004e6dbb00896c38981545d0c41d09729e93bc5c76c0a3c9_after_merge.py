def validate_top_level_object(config):
    if not isinstance(config, dict):
        raise ConfigurationError(
            "Top level object needs to be a dictionary. Check your .yml file "
            "that you have defined a service at the top level.")
    validate_service_names(config)