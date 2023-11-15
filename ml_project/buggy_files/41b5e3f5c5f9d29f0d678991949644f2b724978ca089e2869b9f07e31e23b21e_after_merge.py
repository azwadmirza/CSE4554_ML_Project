def __virtual__():
    if not HAS_ODBC:
        return False, 'Could not import odbc returner; pyodbc is not installed.'
    return True