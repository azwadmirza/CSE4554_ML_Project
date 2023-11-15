def validate_configuration(config, schema):
    """Validate data from configuration.yaml.

    We use voluptuous to validate the data obtained from the
    configuration file with the schema declared above. Voluptuous
    will raise a 'voluptuous.MultipleInvalid' exception if the data
    passed doesn't match the schema.

    This is a helper function so we don't need to do much with it other than
    initialize voluptuous.Schema and attempt to validate the data. The function
    'load_config_file' located on 'opsdroid.configuration.__init__' will handle
    the case when the exception is raised.

    Args:
        config: a yaml stream obtained from opening configuration.yaml
        schema (dict): the rules used to validate against data

    """
    validate = Schema(schema, extra=ALLOW_EXTRA)
    try:
        return validate(config)
    except MultipleInvalid as error:
        _LOGGER.critical(
            _("Configuration for %s failed validation! %s - '%s'."),
            config.get("name", "basic opsdroid rules"),
            error.msg.capitalize(),
            error.path[0],
        )
        sys.exit(1)