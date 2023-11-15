def is_acme_error(err):
    """Check if argument is an ACME error."""
    if isinstance(err, Error) and (err.typ is not None):
        return (ERROR_PREFIX in err.typ) or (OLD_ERROR_PREFIX in err.typ)
    else:
        return False