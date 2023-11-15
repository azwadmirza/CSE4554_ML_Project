    def __run_transaction(self, fun: Callable[[sqlite3.Connection, Any, Any], Any], *args, **kwargs):
        self.connection.execute('begin')
        try:
            result = fun(self.connection, *args, **kwargs)  # type: ignore
            self.connection.commit()
            return result
        except (Exception, OSError): # as e:
            #log.exception('Error running transaction:', exc_info=e)
            self.connection.rollback()
            raise