    def execute_fetchall(self, sql: str, parameters: Iterable = None) -> Awaitable[Iterable[sqlite3.Row]]:
        parameters = parameters if parameters is not None else []
        def __fetchall(conn: sqlite3.Connection, *args, **kwargs):
            return conn.execute(*args, **kwargs).fetchall()
        return wrap_future(self.executor.submit(__fetchall, self.connection, sql, parameters))