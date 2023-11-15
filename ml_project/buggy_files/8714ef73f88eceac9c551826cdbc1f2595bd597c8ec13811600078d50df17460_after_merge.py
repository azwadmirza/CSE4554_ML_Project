    def register_predictors(self, model_data_arr):
        for model_meta in model_data_arr:
            name = self._escape_table_name(model_meta['name'])
            stats = model_meta['data_analysis']
            if 'columns_to_ignore' in stats:
                del stats['columns_to_ignore']
            columns_sql = ','.join(self._to_clickhouse_table(stats, model_meta['predict']))
            columns_sql += ',`select_data_query` Nullable(String)'
            columns_sql += ',`external_datasource` Nullable(String)'
            for col in model_meta['predict']:
                columns_sql += f',`{col}_confidence` Nullable(Float64)'
                if model_meta['data_analysis'][col]['typing']['data_type'] == 'Numeric':
                    columns_sql += f',`{col}_min` Nullable(Float64)'
                    columns_sql += f',`{col}_max` Nullable(Float64)'
                columns_sql += f',`{col}_explain` Nullable(String)'

            msqyl_conn = self.config['api']['mysql']['host'] + ':' + str(self.config['api']['mysql']['port'])
            msqyl_pass = self.config['api']['mysql']['password']
            msqyl_user = self._get_mysql_user()

            q = f"""
                    CREATE TABLE mindsdb.{name}
                    ({columns_sql}
                    ) ENGINE=MySQL('{msqyl_conn}', 'mindsdb', {name}, '{msqyl_user}', '{msqyl_pass}')
            """
            self._query(q)