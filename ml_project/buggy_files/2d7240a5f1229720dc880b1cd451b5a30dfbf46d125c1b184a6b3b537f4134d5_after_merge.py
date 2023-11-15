def read_journal(context, journal_name="default"):
    configuration = load_config(context.config_path)
    with open(configuration["journals"][journal_name]) as journal_file:
        journal = journal_file.read()
    return journal