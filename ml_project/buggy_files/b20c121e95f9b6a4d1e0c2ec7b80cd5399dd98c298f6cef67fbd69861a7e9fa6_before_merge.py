def _unescape_str(text):
    """
    Unescapes a string according the TOML spec. Raises BadEscapeCharacter when appropriate.
    """

    # Detect bad escape jobs
    bad_escape_regexp = re.compile(r'([^\\]|^)\\[^btnfr"\\uU]')
    if bad_escape_regexp.findall(text):
        raise BadEscapeCharacter

    # Do the unescaping
    if six.PY2:
        return _unicode_escaped_string(text).decode('string-escape').decode('unicode-escape')
    else:
        return codecs.decode(_unicode_escaped_string(text), 'unicode-escape')