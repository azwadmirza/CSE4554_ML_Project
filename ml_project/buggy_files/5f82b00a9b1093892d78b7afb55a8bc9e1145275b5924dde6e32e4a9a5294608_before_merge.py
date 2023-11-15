def is_acme_error(err):
    """Check if argument is an ACME error."""
    return (ERROR_PREFIX in str(err)) or (OLD_ERROR_PREFIX in str(err))