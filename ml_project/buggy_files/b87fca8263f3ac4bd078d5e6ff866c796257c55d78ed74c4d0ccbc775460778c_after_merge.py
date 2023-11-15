def __virtual__():
    if not HAS_REDIS:
        return False, 'Could not import redis returner; ' \
                      'redis python client is not installed.'
    return __virtualname__