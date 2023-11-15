    def __init__(self, msg, error):
        super().__init__(msg)
        self.error = error

        log.sql.debug("SQL error:")
        log.sql.debug("type: {}".format(
            debug.qenum_key(QSqlError, error.type())))
        log.sql.debug("database text: {}".format(error.databaseText()))
        log.sql.debug("driver text: {}".format(error.driverText()))
        log.sql.debug("error code: {}".format(error.nativeErrorCode()))

        # https://sqlite.org/rescode.html
        # https://github.com/qutebrowser/qutebrowser/issues/2930
        # https://github.com/qutebrowser/qutebrowser/issues/3004
        environmental_errors = [
            '8',   # SQLITE_READONLY
            '9',   # SQLITE_LOCKED,
            '13',  # SQLITE_FULL,
        ]
        self.environmental = error.nativeErrorCode() in environmental_errors