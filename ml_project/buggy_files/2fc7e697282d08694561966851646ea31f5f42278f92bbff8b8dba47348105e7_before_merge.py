def __virtual__():
    if not HAS_DJANGO:
        return False
    return True