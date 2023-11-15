    def reject_all(self, include_accepted=False):
        '''
        Reject all keys
        '''
        self.reject('*', include_accepted=include_accepted)