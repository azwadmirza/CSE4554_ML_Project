    def accept_all(self, include_rejected=False):
        '''
        Accept all keys
        '''
        self.accept('*', include_rejected=include_rejected)