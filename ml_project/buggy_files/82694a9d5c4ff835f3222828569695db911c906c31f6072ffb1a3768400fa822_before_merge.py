def local(value):
    """Mark a file as local file. This disables application of a default remote
    provider.
    """
    if is_flagged(value, "remote"):
        raise SyntaxError("Remote and local flags are mutually exclusive.")
    return flag(value, "local")