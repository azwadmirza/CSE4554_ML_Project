    def register_predictors(self, model_data_arr):
        for model_meta in model_data_arr:
            name = model_meta['name']
            stats = model_meta['data_analysis']
            columns_sql = ','.join(self._to_mariadb_table(stats, model_meta['predict']))
            columns_sql += ',`select_data_query` varchar(500)'
            columns_sql += ',`external_datasource` varchar(500)'
            for col in model_meta['predict']:
                columns_sql += f',`{col}_confidence` double'
                if model_meta['data_analysis'][col]['typing']['data_type'] == 'Numeric':
                    columns_sql += f',`{col}_min` double'
                    columns_sql += f',`{col}_max` double'
                columns_sql += f',`{col}_explain` varchar(500)'

            connect = self._get_connect_string(name)

            q = f"""
                    CREATE TABLE mindsdb.{self._escape_table_name(name)}
                    ({columns_sql}
                    ) ENGINE=CONNECT TABLE_TYPE=MYSQL CONNECTION='{connect}';
            """
            self._query(q)