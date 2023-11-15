    def failed(self):
        ''' ``True`` if code execution failed

        '''
        return self._failed or self._code is None