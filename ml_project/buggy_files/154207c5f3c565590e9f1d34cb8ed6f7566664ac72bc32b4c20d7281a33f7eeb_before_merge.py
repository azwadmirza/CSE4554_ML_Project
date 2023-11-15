    def _collect_info(self, engine_or_conn, selectable, columns, test_rows):
        from sqlalchemy import sql

        # fetch test DataFrame
        if columns:
            query = sql.select([sql.column(c) for c in columns], from_obj=selectable).limit(test_rows)
        else:
            query = sql.select('*', from_obj=selectable).limit(test_rows)
        test_df = pd.read_sql(query, engine_or_conn, index_col=self._index_col,
                              coerce_float=self._coerce_float,
                              parse_dates=self._parse_dates)
        self._row_memory_usage = \
            test_df.memory_usage(deep=True, index=True).sum() / test_rows

        if self._method == 'offset':
            # fetch size
            size = list(engine_or_conn.execute(
                sql.select([sql.func.count()]).select_from(selectable)))[0][0]
            shape = (size, test_df.shape[1])
        else:
            shape = (np.nan, test_df.shape[1])

        return test_df, shape