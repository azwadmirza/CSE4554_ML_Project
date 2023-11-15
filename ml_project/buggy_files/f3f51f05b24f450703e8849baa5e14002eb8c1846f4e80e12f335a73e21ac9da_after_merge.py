    def unregister_predictor(self, name):
        q = f"""
            drop table if exists mindsdb.{self._escape_table_name(name)};
        """
        self._query(q)