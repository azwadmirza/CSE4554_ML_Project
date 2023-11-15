    def insert_batch(self, values, replace=False):
        """Performantly append multiple rows to the table.

        Args:
            values: A dict with a list of values to insert for each field name.
            replace: If true, overwrite rows with a primary key match.
        """
        q = self._insert_query(values, replace)
        for key, val in values.items():
            q.bindValue(':{}'.format(key), val)

        db = QSqlDatabase.database()
        db.transaction()
        if not q.execBatch():
            raise SqliteError.from_query('exec', q.lastQuery(), q.lastError())
        db.commit()
        self.changed.emit()