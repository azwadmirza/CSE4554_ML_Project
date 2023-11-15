    def __init__(self, querystr, forward_only=True):
        """Prepare a new sql query.

        Args:
            querystr: String to prepare query from.
            forward_only: Optimization for queries that will only step forward.
                          Must be false for completion queries.
        """
        super().__init__(QSqlDatabase.database())
        log.sql.debug('Preparing SQL query: "{}"'.format(querystr))
        if not self.prepare(querystr):
            _handle_query_error('prepare', querystr, self.lastError())
        self.setForwardOnly(forward_only)