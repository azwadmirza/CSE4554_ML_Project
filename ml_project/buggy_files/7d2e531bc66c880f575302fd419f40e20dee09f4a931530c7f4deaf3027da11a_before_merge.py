def open_journal(journal_name="default"):
    config = load_config(install.CONFIG_FILE_PATH)
    journal_conf = config["journals"][journal_name]

    # We can override the default config on a by-journal basis
    if type(journal_conf) is dict:
        config.update(journal_conf)
    # But also just give them a string to point to the journal file
    else:
        config["journal"] = journal_conf

    return Journal.open_journal(journal_name, config)