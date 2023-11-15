def __virtual__():
    if not HAS_SQLITE3:
        return False, 'Could not import sqlite3 returner; sqlite3 is not installed.'
    return __virtualname__