def is_special(key, modifiers):
    """Check whether this key requires special key syntax."""
    _assert_plain_key(key)
    _assert_plain_modifier(modifiers)
    return not (_is_printable(key) and
                modifiers in [Qt.ShiftModifier, Qt.NoModifier,
                              Qt.KeypadModifier])