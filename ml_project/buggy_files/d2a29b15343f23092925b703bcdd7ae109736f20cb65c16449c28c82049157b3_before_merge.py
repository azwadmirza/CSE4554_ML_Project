    def run(self, **values):
        """Execute the prepared query."""
        log.sql.debug('Running SQL query: "{}"'.format(self.lastQuery()))
        for key, val in values.items():
            self.bindValue(':{}'.format(key), val)
        log.sql.debug('query bindings: {}'.format(self.boundValues()))
        if not self.exec_():
            _handle_query_error('exec', self.lastQuery(), self.lastError())
        return self