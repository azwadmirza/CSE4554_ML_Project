def config_var(context, key, value="", journal=None):
    value = read_value_from_string(value or context.text or "")
    configuration = load_config(context.config_path)

    if journal:
        configuration = configuration["journals"][journal]

    assert key in configuration
    assert configuration[key] == value