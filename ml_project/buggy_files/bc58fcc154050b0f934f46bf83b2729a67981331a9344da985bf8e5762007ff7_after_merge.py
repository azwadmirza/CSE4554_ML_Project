def find_insert_position(accounts, date, insert_options, filenames):
    """Find insert position for an account.

    Args:
        accounts: A list of accounts.
        date: A date. Only InsertOptions before this date will be considered.
        insert_options: A list of InsertOption.
        filenames: List of Beancount files.
    """
    for account in accounts:
        for insert_option in insert_options:
            if insert_option.date >= date:
                break
            if insert_option.re.match(account):
                return (insert_option.filename, insert_option.lineno - 1)

    return (
        filenames[0],
        len(open(filenames[0], encoding="utf-8").readlines()) + 1,
    )