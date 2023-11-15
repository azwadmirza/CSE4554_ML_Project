def check_not_journal_content(context, text, journal_name="default"):
    journal = read_journal(context, journal_name)
    assert text not in journal, journal