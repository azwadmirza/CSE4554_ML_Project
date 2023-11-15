def _is_surrogate(key):
    """Check for Unicode characters such as emoji and extended CJK characters
    Necessary to work around poor handling of higher codepoints by QKeyEvent
    This checks for unicode codepoints above ASCII range. The highest unicode
    is below Qt::Key modifiers and "special" keys, which start at 0x1000000
    """
    return 0xd800 <= key <= 0xdfff