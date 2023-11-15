def is_prefix_valid(text, offset, language):
    """Check if current offset prefix is valid."""
    # Account for length differences in text when using characters
    # such as emojis in the editor.
    # Fixes spyder-ide/spyder#11862
    utf16_diff = qstring_length(text) - len(text)
    current_pos_text = text[offset - utf16_diff - 1]

    empty_start = empty_regex.match(current_pos_text) is not None
    max_end = -1
    regex = LANGUAGE_REGEX.get(language.lower(), all_regex)
    prefix = ''

    for match in regex.finditer(text):
        start, end = match.span()
        max_end = max(end, max_end)
        if offset >= start and offset <= end:
            prefix = match.group()
    if offset > max_end:
        if letter_regex.match(current_pos_text):
            prefix = current_pos_text
    valid = prefix != '' or (prefix == '' and empty_start)
    return valid