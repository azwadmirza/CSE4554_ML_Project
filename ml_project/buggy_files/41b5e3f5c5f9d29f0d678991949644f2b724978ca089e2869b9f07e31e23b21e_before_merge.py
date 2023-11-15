def __virtual__():
    if not HAS_ODBC:
        return False
    return True