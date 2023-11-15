    def record_many_sql(sql, param_list, cursor):
        for params in param_list:
            record_sql(sql, params, cursor)