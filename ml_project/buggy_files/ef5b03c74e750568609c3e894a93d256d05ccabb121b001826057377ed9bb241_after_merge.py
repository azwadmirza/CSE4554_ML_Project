def _remap_unicode(key, text):
    """Work around QtKeyEvent's bad values for high codepoints.

    QKeyEvent handles higher unicode codepoints poorly (see
    QTBUG-72776). It uses UTF-16 to handle key events, and for
    higher codepoints that require UTF-16 surrogates (e.g. emoji
    and some CJK characters), it sets the keycode to just the
    upper half of the surrogate, which renders it useless, and
    breaks UTF-8 encoding, causing crashes. So we detect this
    case, and reassign the key code to be the full Unicode
    codepoint, which we can recover from the text() property,
    wihch has the full character."""
    if _is_surrogate(key):
        if len(text) != 1:
            raise KeyParseError(text, "Key had too many characters!")
        else:
            return ord(text[0])
    else:
        return key