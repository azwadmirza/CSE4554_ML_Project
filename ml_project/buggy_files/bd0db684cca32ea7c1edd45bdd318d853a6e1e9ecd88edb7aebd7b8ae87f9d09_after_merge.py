    def executemany(self, sql, param_list):
        try:
            return real_executemany(self, sql, param_list)
        finally:
            record_many_sql(sql, param_list, self.cursor)