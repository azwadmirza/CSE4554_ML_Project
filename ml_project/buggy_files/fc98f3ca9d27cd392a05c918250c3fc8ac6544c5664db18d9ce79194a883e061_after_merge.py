def raise_sqlite_error(msg, error):
    """Raise either a SqlBugError or SqlKnownError."""
    error_code = error.nativeErrorCode()
    database_text = error.databaseText()
    driver_text = error.driverText()

    log.sql.debug("SQL error:")
    log.sql.debug("type: {}".format(
        debug.qenum_key(QSqlError, error.type())))
    log.sql.debug("database text: {}".format(database_text))
    log.sql.debug("driver text: {}".format(driver_text))
    log.sql.debug("error code: {}".format(error_code))

    environmental_errors = [
        SqliteErrorCode.BUSY,
        SqliteErrorCode.READONLY,
        SqliteErrorCode.IOERR,
        SqliteErrorCode.CORRUPT,
        SqliteErrorCode.FULL,
        SqliteErrorCode.CANTOPEN,
    ]

    # WORKAROUND for https://bugreports.qt.io/browse/QTBUG-70506
    # We don't know what the actual error was, but let's assume it's not us to
    # blame... Usually this is something like an unreadable database file.
    qtbug_70506 = (error_code == SqliteErrorCode.UNKNOWN and
                   driver_text == "Error opening database" and
                   database_text == "out of memory")

    # https://github.com/qutebrowser/qutebrowser/issues/4681
    # If the query we built was too long
    too_long_err = (
        error_code == SqliteErrorCode.ERROR and
        driver_text == "Unable to execute statement" and
        (database_text.startswith("Expression tree is too large") or
         database_text == "too many SQL variables"))

    if (error_code in environmental_errors or qtbug_70506 or too_long_err):
        raise SqlKnownError(msg, error)

    raise SqlBugError(msg, error)