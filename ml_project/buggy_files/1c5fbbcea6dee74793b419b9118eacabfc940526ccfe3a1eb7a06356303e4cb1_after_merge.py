def __virtual__():
    if not HAS_PG:
        return False, 'Could not import pgjsonb returner; python-psycopg2 is not installed.'
    return True