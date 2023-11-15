    def execute(self, sql, params=None):
        try:
            return real_execute(self, sql, params)
        finally:
            record_sql(sql, params)