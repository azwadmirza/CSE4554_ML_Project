def __virtual__():
    if not HAS_MEMCACHE:
        return False, 'Could not import memcache returner; ' \
                      'memcache python client is not installed.'
    return __virtualname__