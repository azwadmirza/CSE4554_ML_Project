def config_no_var(context, key, value="", journal=None):
    config = load_config(install.CONFIG_FILE_PATH)

    if journal:
        config = config["journals"][journal]

    assert key not in config