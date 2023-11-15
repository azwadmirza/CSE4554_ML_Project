def reraise_errors(msg='{0!r}', errors=None):
    """Context reraising crypto errors as :exc:`SecurityError`."""
    assert crypto is not None
    errors = (crypto.Error,) if errors is None else errors
    try:
        yield
    except errors as exc:
        reraise(SecurityError,
                SecurityError(msg.format(exc)),
                sys.exc_info()[2])