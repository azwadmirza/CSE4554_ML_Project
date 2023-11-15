    def executemany(self, sql: str, params: Iterable):
        params = params if params is not None else []
        # this fetchall is needed to prevent SQLITE_MISUSE
        return self.run(lambda conn: conn.executemany(sql, params).fetchall())