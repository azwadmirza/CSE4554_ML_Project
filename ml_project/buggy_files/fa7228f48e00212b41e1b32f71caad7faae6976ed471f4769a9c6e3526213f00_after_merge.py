    def __init__(self, table=None, client=None):
        """
        table : `astropy.table.Table`
        """
        super().__init__()
        self.table = table or astropy.table.QTable()
        self.query_args = getattr(table, 'query_args', None)
        self.requests = getattr(table, 'requests', None)
        self._client = client