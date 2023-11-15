def load_config_file(config_paths):
    """Load a yaml config file from path.

    We get a path for the configuration file and then use the yaml
    library to load this file - the configuration will be shown as a
    dict.  Here we also add constructors to our yaml loader and handle
    different exceptions that could be raised when trying to load or
    validate the file.

    Args:
        config_paths: List of paths to configuration.yaml files

    Returns:
        dict: Dict containing config fields

    """

    config_path = get_config_path(config_paths)

    yaml.SafeLoader.add_implicit_resolver("!envvar", env_var_pattern, first="$")
    yaml.SafeLoader.add_constructor("!envvar", envvar_constructor)

    try:
        with open(config_path, "r") as stream:
            _LOGGER.info(_("Loaded config from %s."), config_path)

            data = yaml.load(stream, Loader=yaml.SafeLoader)
            validate_data_type(data)

            configuration = update_pre_0_17_config_format(data)
            validate_configuration(configuration, BASE_SCHEMA)

            return configuration

    except yaml.YAMLError as error:
        _LOGGER.critical(error)
        sys.exit(1)

    except FileNotFoundError as error:
        _LOGGER.critical(error)
        sys.exit(1)

    except TypeError as error:
        _LOGGER.critical(error)
        sys.exit(1)