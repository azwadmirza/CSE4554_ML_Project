def __virtual__():
    if not HAS_PYMONGO:
        return False, 'Could not import mongo returner; pymongo is not installed.'
    return __virtualname__