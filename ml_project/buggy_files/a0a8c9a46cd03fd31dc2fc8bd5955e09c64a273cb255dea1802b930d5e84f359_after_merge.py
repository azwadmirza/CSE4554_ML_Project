def init(db_path):
    """Initialize the SQL database connection."""
    database = QSqlDatabase.addDatabase('QSQLITE')
    if not database.isValid():
        raise SqlKnownError('Failed to add database. Are sqlite and Qt '
                            'sqlite support installed?')
    database.setDatabaseName(db_path)
    if not database.open():
        error = database.lastError()
        msg = "Failed to open sqlite database at {}: {}".format(db_path,
                                                                error.text())
        raise_sqlite_error(msg, error)

    # Enable write-ahead-logging and reduce disk write frequency
    # see https://sqlite.org/pragma.html and issues #2930 and #3507
    Query("PRAGMA journal_mode=WAL").run()
    Query("PRAGMA synchronous=NORMAL").run()