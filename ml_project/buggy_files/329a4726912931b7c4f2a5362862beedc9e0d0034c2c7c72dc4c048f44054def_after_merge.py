def check_journal_entries(context, number, journal_name="default"):
    journal = open_journal(context, journal_name)
    assert len(journal.entries) == number