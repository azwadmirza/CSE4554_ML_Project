    def error(self):
        ''' If code execution fails, may contain a related error message.

        '''
        return self._error if self._permanent_error is None else self._permanent_error