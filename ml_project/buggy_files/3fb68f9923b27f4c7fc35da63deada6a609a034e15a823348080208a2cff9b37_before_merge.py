def __virtual__():
    if not HAS_MYSQL:
        return False
    return True