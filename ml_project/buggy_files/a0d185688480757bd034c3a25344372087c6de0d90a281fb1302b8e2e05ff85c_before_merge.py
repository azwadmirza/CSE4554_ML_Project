def is_prefix_valid(text, offset, language):
    """Check if current offset prefix is valid."""
    regex = LANGUAGE_REGEX.get(language.lower(), all_regex)
    prefix = ''
    current_pos_text = text[offset - 1]
    empty_start = empty_regex.match(current_pos_text) is not None
    max_end = -1
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