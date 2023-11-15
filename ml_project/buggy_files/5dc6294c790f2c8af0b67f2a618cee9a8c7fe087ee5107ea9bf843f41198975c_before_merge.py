def __virtual__():
    if not HAS_PYMONGO:
        return False
    return 'mongo_return'