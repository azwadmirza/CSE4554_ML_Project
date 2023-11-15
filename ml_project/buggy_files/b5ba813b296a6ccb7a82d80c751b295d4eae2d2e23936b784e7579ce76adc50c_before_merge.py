def _parse_oneof_validator(error):
    """oneOf has multiple schemas, so we need to reason about which schema, sub
    schema or constraint the validation is failing on.
    Inspecting the context value of a ValidationError gives us information about
    which sub schema failed and which kind of error it is.
    """
    types = []
    for context in error.context:

        if context.validator == 'oneOf':
            _, error_msg = _parse_oneof_validator(context)
            return path_string(context.path), error_msg

        if context.validator == 'required':
            return (None, context.message)

        if context.validator == 'additionalProperties':
            invalid_config_key = parse_key_from_error_msg(context)
            return (None, "contains unsupported option: '{}'".format(invalid_config_key))

        if context.path:
            return (
                path_string(context.path),
                "contains {}, which is an invalid type, it should be {}".format(
                    json.dumps(context.instance),
                    _parse_valid_types_from_validator(context.validator_value)),
            )

        if context.validator == 'uniqueItems':
            return (
                None,
                "contains non unique items, please remove duplicates from {}".format(
                    context.instance),
            )

        if context.validator == 'type':
            types.append(context.validator_value)

    valid_types = _parse_valid_types_from_validator(types)
    return (None, "contains an invalid type, it should be {}".format(valid_types))