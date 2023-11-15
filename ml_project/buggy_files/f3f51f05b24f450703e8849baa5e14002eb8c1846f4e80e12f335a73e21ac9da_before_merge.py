    def unregister_predictor(self, name):
        q = f"""
            drop table if exists mindsdb.{name};
        """
        self._query(q)