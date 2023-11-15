    def _execute_insert_multi(self, conn, keys, data_iter):
        """Alternative to _execute_insert for DBs support multivalue INSERT.

        Note: multi-value insert is usually faster for analytics DBs
        and tables containing a few columns
        but performance degrades quickly with increase of columns.
        """
        data = [dict(zip(keys, row)) for row in data_iter]
        conn.execute(self.table.insert(data))