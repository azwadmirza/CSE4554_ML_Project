    def load_data(self, table_name, obj, database=None, **kwargs):
        """Load data into a given table.

        Wraps the LOAD DATA DDL statement. Loads data into an OmniSciDB table
        by physically moving data files.

        Parameters
        ----------
        table_name : string
        obj: pandas.DataFrame or pyarrow.Table
        database : string, optional
        """
        _database = self.db_name
        self.set_database(database)
        self.con.load_table(table_name, obj)
        self.set_database(_database)