def journal_doesnt_exist(context, journal_name="default"):
    configuration = load_config(context.config_path)

    journal_path = configuration["journals"][journal_name]
    assert not os.path.exists(journal_path)