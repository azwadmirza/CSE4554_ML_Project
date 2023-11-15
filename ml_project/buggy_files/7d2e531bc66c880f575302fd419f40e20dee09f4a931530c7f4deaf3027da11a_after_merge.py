def open_journal(context, journal_name="default"):
    configuration = load_config(context.config_path)
    journal_conf = configuration["journals"][journal_name]

    # We can override the default config on a by-journal basis
    if type(journal_conf) is dict:
        configuration.update(journal_conf)
    # But also just give them a string to point to the journal file
    else:
        configuration["journal"] = journal_conf

    return Journal.open_journal(journal_name, configuration)