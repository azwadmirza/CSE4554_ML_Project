def get_entry_slice(entry):
    """Get slice of the source file for an entry.

    Args:
        entry: An entry.

    Returns:
        A string containing the lines of the entry and the `sha256sum` of
        these lines.

    Raises:
        FavaAPIException: If the file at `path` is not one of the
            source files.

    """
    with open(entry.meta["filename"], mode="r", encoding="utf-8") as file:
        lines = file.readlines()

    entry_lines = find_entry_lines(lines, entry.meta["lineno"] - 1)
    entry_source = "".join(entry_lines).rstrip("\n")
    sha256sum = sha256(codecs.encode(entry_source)).hexdigest()

    return entry_source, sha256sum