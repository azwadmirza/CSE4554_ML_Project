def __virtual__():
    if not HAS_POSTGRES:
        return False, 'Could not import postgres returner; psycopg2 is not installed.'
    return __virtualname__