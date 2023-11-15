def insert_entry(entry, filenames, fava_options):
    """Insert an entry.

    Args:
        entry: An entry.
        filenames: List of filenames.
        fava_options: The ledgers fava_options. Note that the line numbers of
            the insert options might be updated.
    """
    insert_options = fava_options.get("insert-entry", [])
    if isinstance(entry, data.Transaction):
        accounts = reversed([p.account for p in entry.postings])
    else:
        accounts = [entry.account]
    filename, lineno = find_insert_position(
        accounts, entry.date, insert_options, filenames
    )
    content = _format_entry(entry, fava_options) + "\n"

    with open(filename, "r") as file:
        contents = file.readlines()

    contents.insert(lineno, content)

    with open(filename, "w") as file:
        file.writelines(contents)

    for index, option in enumerate(insert_options):
        added_lines = content.count("\n") + 1
        if option.filename == filename and option.lineno > lineno:
            insert_options[index] = option._replace(
                lineno=lineno + added_lines
            )