def __virtual__():
    if not HAS_PYCASSA:
        return False, 'Could not import cassandra returner; pycassa is not installed.'
    return __virtualname__