def version():
    """Return the sqlite version string."""
    try:
        if not QSqlDatabase.database().isOpen():
            init(':memory:')
            ver = Query("select sqlite_version()").run().value()
            close()
            return ver
        return Query("select sqlite_version()").run().value()
    except SqlKnownError as e:
        return 'UNAVAILABLE ({})'.format(e)