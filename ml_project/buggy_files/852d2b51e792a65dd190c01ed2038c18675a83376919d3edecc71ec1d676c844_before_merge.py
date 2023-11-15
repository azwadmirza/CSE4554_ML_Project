    def is_disconnect(self, e, connection, cursor):
        if isinstance(e, self.dbapi.Error):
            for code in (
                "08S01",
                "01002",
                "08003",
                "08007",
                "08S02",
                "08001",
                "HYT00",
                "HY010",
                "10054",
            ):
                if code in str(e):
                    return True
        return super(MSDialect_pyodbc, self).is_disconnect(
            e, connection, cursor
        )