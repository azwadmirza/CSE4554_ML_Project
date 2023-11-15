    def error_detail(self):
        ''' If code execution fails, may contain a traceback or other details.

        '''
        return self._error_detail if self._permanent_error_detail is None else self._permanent_error_detail