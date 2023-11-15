def journal_doesnt_exist(context, journal_name="default"):
    config = load_config(install.CONFIG_FILE_PATH)

    journal_path = config["journals"][journal_name]
    assert not os.path.exists(journal_path)