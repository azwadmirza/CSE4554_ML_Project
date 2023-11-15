    def record_many_sql(sql, param_list):
        for params in param_list:
            record_sql(sql, params)