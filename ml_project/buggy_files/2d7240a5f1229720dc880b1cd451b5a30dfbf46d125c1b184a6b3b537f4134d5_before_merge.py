def read_journal(journal_name="default"):
    config = load_config(install.CONFIG_FILE_PATH)
    with open(config["journals"][journal_name]) as journal_file:
        journal = journal_file.read()
    return journal