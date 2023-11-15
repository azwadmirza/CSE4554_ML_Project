    def _set(self, type, offset, values):
        '''

        :param key: The type prefix to use
        :param offset: The address offset to start at
        :param values: The values to set
        '''
        if self._check(type, offset, values):
            context = self._build_set(type, offset, values)
            query = self._table.insert()
            result = self._connection.execute(query, context)
            return result.rowcount == len(values)
        else:
            return False