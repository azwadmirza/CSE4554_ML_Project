def journal_exists(context, journal_name="default"):
    configuration = load_config(context.config_path)

    journal_path = configuration["journals"][journal_name]
    assert os.path.exists(journal_path)