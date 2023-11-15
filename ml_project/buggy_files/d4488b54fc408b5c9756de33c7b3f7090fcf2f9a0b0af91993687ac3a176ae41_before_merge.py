def data_processer(raw_data, logger):
    """
    Groups dictionaries by datetime key.
    Removes unneeded keys and logs any new ones.
    Returns a list of tuples containing (datetime object, dictionary).
    """

    dt_key = lambda x: x['datetime']
    grouped = groupby(raw_data, dt_key)

    keys_to_ignore = {'Load', 'Net Purchases', 'Inadvertent', 'PURPA Other'}
    known_keys = GENERATION_MAPPING.keys() | keys_to_ignore

    unmapped = set()
    parsed_data = []
    for group in grouped:
        dt = timestamp_converter(group[0])
        generation = group[1]

        production = {}
        for gen_type in generation:
            production[gen_type['name']] = float(gen_type['data'])

        current_keys = production.keys() | set()
        unknown_keys = current_keys - known_keys
        unmapped = unmapped | unknown_keys

        keys_to_remove = keys_to_ignore | unknown_keys

        for key in keys_to_remove:
            production.pop(key)

        production = {GENERATION_MAPPING[k]: v for k, v in production.items()}

        parsed_data.append((dt, production))

    for key in unmapped:
        logger.warning('Key \'{}\' in US-IPC is not mapped to type.'.format(key), extra={'key': 'US-IPC'})

    return parsed_data