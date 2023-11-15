def __virtual__():
    if not HAS_DJANGO:
        return False, 'Could not import django returner; django is not installed.'
    return True