    def run_batch(self, values):
        """Execute the query in batch mode."""
        log.sql.debug('Running SQL query (batch): "{}"'.format(
            self.query.lastQuery()))

        self._bind_values(values)

        db = QSqlDatabase.database()
        ok = db.transaction()
        self._check_ok('transaction', ok)

        ok = self.query.execBatch()
        try:
            self._check_ok('execBatch', ok)
        except SqlError:
            # Not checking the return value here, as we're failing anyways...
            db.rollback()
            raise

        ok = db.commit()
        self._check_ok('commit', ok)