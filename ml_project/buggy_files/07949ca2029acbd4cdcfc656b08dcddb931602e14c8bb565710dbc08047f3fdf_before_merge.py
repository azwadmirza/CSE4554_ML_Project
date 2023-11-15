    def load_data(
        self, table_name, path, database=None, overwrite=False, partition=None
    ):
        """
        Wraps the LOAD DATA DDL statement. Loads data into an Impala table by
        physically moving data files.

        Parameters
        ----------
        table_name : string
        database : string, default None (optional)
        """
        table = self.table(table_name, database=database)
        return table.load_data(path, overwrite=overwrite, partition=partition)