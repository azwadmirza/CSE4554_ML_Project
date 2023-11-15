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