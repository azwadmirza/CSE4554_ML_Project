def save_entry_slice(entry, source_slice, sha256sum):
    """Save slice of the source file for an entry.

    Args:
        entry: An entry.
        source_slice: The lines that the entry should be replaced with.
        sha256sum: The sha256sum of the current lines of the entry.

    Returns:
        The `sha256sum` of the new lines of the entry.

    Raises:
        FavaAPIException: If the file at `path` is not one of the
            source files.

    """

    with open(entry.meta["filename"], "r") as file:
        lines = file.readlines()

    first_entry_line = entry.meta["lineno"] - 1
    entry_lines = find_entry_lines(lines, first_entry_line)
    entry_source = "".join(entry_lines).rstrip("\n")
    original_sha256sum = sha256(codecs.encode(entry_source)).hexdigest()
    if original_sha256sum != sha256sum:
        raise FavaAPIException("The file changed externally.")

    lines = (
        lines[:first_entry_line]
        + [source_slice + "\n"]
        + lines[first_entry_line + len(entry_lines) :]
    )
    with open(entry.meta["filename"], "w") as file:
        file.writelines(lines)

    return sha256(codecs.encode(source_slice)).hexdigest()