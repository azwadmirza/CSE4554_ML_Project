    def _update(self, type, offset, values):
        '''

        :param type: The type prefix to use
        :param offset: The address offset to start at
        :param values: The values to set
        '''
        context = self._build_set(type, offset, values, prefix='x_')
        query = self._table.update().values(name='value')
        query = query.where(and_(
            self._table.c.type == bindparam('x_type'),
            self._table.c.index == bindparam('x_index')))
        result = self._connection.execute(query, context)
        return result.rowcount == len(values)