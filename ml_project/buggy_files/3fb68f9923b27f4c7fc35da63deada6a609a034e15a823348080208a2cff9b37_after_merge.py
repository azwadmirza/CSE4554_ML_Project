def __virtual__():
    if not HAS_MYSQL:
        return False, 'Could not import mysql returner; ' \
                      'mysql python client is not installed.'
    return True