    def executemany(self, sql: str, params: Iterable):
        def __executemany_in_a_transaction(conn: sqlite3.Connection, *args, **kwargs):
            return conn.executemany(*args, **kwargs)
        return self.run(__executemany_in_a_transaction, sql, params)