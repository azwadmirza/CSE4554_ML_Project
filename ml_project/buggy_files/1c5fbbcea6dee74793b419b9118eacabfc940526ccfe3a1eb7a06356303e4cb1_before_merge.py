def __virtual__():
    if not HAS_PG:
        return False
    return True