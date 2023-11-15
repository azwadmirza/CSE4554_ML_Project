    def _validate(self, type, offset, count):
        '''
        :param key: The key prefix to use
        :param offset: The address offset to start at
        :param count: The number of bits to read
        :returns: The result of the validation
        '''
        query = self._table.select(and_(
            self._table.c.type == type,
            self._table.c.index >= offset,
            self._table.c.index <= offset + count - 1))
        result = self._connection.execute(query).fetchall()
        return len(result) == count