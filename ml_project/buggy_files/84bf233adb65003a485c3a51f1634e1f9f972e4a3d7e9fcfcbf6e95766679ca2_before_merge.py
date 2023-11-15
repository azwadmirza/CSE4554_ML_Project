def __virtual__():
    if not HAS_SQLITE3:
        return False
    return __virtualname__