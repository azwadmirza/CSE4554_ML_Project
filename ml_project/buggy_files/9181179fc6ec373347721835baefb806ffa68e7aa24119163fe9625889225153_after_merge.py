def init(db_path):
    """Initialize the SQL database connection."""
    database = QSqlDatabase.addDatabase('QSQLITE')
    if not database.isValid():
        raise SqlError('Failed to add database. '
                       'Are sqlite and Qt sqlite support installed?',
                       environmental=True)
    database.setDatabaseName(db_path)
    if not database.open():
        error = database.lastError()
        raise SqliteError("Failed to open sqlite database at {}: {}"
                          .format(db_path, error.text()), error)

    # Enable write-ahead-logging and reduce disk write frequency
    # see https://sqlite.org/pragma.html and issues #2930 and #3507
    Query("PRAGMA journal_mode=WAL").run()
    Query("PRAGMA synchronous=NORMAL").run()