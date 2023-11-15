    def _build_set(self, type, offset, values, prefix=''):
        ''' A helper method to generate the sql update context

        :param type: The key prefix to use
        :param offset: The address offset to start at
        :param values: The values to set
        :param prefix: Prefix fields index and type, defaults to empty string
        '''
        result = []
        for index, value in enumerate(values):
            result.append({
                prefix + 'type': type,
                prefix + 'index': offset + index,
                'value': value
            })
        return result