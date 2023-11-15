def config_no_var(context, key, value="", journal=None):
    configuration = load_config(context.config_path)

    if journal:
        configuration = configuration["journals"][journal]

    assert key not in configuration