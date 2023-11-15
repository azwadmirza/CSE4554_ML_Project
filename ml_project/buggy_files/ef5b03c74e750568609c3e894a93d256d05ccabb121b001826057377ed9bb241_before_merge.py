def _remap_unicode(key, text):
    """Work around Qt having bad values for UTF-16 surrogates
    Qt events have the upper half of the UTF-16 representation as key()
    instead of the unicode codepoint. We re-parse these from text()
    """
    if _is_surrogate(key):
        if len(text) != 1:
            raise KeyParseError(text, "Key had too many characters!")
        else:
            return ord(text[0])
    else:
        return key