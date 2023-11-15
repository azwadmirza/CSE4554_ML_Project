def check_journal_content(context, text, journal_name="default"):
    journal = read_journal(context, journal_name)
    assert text in journal, journal