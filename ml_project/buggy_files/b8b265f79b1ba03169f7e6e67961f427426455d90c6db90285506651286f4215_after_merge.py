    def __run_transaction_with_foreign_keys_disabled(self,
                                                     fun: Callable[[sqlite3.Connection, Any, Any], Any],
                                                     args, kwargs):
        foreign_keys_enabled, = self.connection.execute("pragma foreign_keys").fetchone()
        if not foreign_keys_enabled:
            raise sqlite3.IntegrityError("foreign keys are disabled, use `AIOSQLite.run` instead")
        try:
            self.connection.execute('pragma foreign_keys=off')
            return self.__run_transaction(fun, *args, **kwargs)
        finally:
            self.connection.execute('pragma foreign_keys=on')