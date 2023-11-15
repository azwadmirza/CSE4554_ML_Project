def validate_config_against_schema(config_schema, config_object, config_path,
                                  pack_name=None):
    """
    Validate provided config dictionary against the provided config schema
    dictionary.
    """
    # NOTE: Lazy improt to avoid performance overhead of importing this module when it's not used
    import jsonschema

    pack_name = pack_name or 'unknown'

    schema = util_schema.get_schema_for_resource_parameters(parameters_schema=config_schema,
                                                            allow_additional_properties=True)
    instance = config_object

    try:
        cleaned = util_schema.validate(instance=instance, schema=schema,
                                       cls=util_schema.CustomValidator, use_default=True,
                                       allow_default_none=True)
    except jsonschema.ValidationError as e:
        attribute = getattr(e, 'path', [])
        attribute = '.'.join(attribute)

        msg = ('Failed validating attribute "%s" in config for pack "%s" (%s): %s' %
               (attribute, pack_name, config_path, str(e)))
        raise jsonschema.ValidationError(msg)

    return cleaned