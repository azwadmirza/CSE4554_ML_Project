def single_line_short_description(schema_or_field, strict=True):
    short_length = len(schema_or_field['field_details']['short'])
    if "\n" in schema_or_field['field_details']['short'] or short_length > SHORT_LIMIT:
        msg = "Short descriptions must be single line, and under {} characters (current length: {}).\n".format(
            SHORT_LIMIT, short_length)
        msg += "Offending field or field set: {}\nShort description:\n  {}".format(
            schema_or_field['field_details']['name'],
            schema_or_field['field_details']['short'])
        if strict:
            raise ValueError(msg)
        else:
            ecs_helpers.strict_warning(msg)