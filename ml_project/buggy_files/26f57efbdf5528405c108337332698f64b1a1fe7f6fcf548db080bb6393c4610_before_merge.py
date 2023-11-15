def journal_exists(context, journal_name="default"):
    config = load_config(install.CONFIG_FILE_PATH)

    journal_path = config["journals"][journal_name]
    assert os.path.exists(journal_path)