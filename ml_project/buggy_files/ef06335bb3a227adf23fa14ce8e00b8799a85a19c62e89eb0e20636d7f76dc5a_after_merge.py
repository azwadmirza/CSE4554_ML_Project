    def _execute_insert(self, conn, keys, data_iter):
        data_list = list(data_iter)
        conn.executemany(self.insert_statement(num_rows=1), data_list)