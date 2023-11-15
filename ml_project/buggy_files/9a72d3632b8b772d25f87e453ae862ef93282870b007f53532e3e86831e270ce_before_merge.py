def field_assertions_and_warnings(field):
    '''Additional checks on a fleshed out field'''
    if not ecs_helpers.is_intermediate(field):
        single_line_short_description(field)
        if field['field_details']['level'] not in ACCEPTABLE_FIELD_LEVELS:
            msg = "Invalid level for field '{}'.\nValue: {}\nAcceptable values: {}".format(
                field['field_details']['name'], field['field_details']['level'],
                ACCEPTABLE_FIELD_LEVELS)
            raise ValueError(msg)