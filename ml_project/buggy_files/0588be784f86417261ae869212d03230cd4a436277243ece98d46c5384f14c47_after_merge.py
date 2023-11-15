def install_sql_hook():
    # type: () -> None
    """If installed this causes Django's queries to be captured."""
    try:
        from django.db.backends.utils import CursorWrapper  # type: ignore
    except ImportError:
        from django.db.backends.util import CursorWrapper  # type: ignore

    try:
        real_execute = CursorWrapper.execute
        real_executemany = CursorWrapper.executemany
    except AttributeError:
        # This won't work on Django versions < 1.6
        return

    def record_many_sql(sql, param_list, cursor):
        for params in param_list:
            record_sql(sql, params, cursor)

    def execute(self, sql, params=None):
        try:
            return real_execute(self, sql, params)
        finally:
            record_sql(sql, params, self.cursor)

    def executemany(self, sql, param_list):
        try:
            return real_executemany(self, sql, param_list)
        finally:
            record_many_sql(sql, param_list, self.cursor)

    CursorWrapper.execute = execute
    CursorWrapper.executemany = executemany
    ignore_logger("django.db.backends")