def config_var(context, key, value="", journal=None):
    value = read_value_from_string(value or context.text or "")
    config = load_config(install.CONFIG_FILE_PATH)

    if journal:
        config = config["journals"][journal]

    assert key in config
    assert config[key] == value