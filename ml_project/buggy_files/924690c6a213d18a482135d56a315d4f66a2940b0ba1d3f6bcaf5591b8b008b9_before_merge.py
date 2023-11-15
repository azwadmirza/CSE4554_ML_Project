    def reject_all(self):
        '''
        Reject all keys
        '''
        self.reject('*', include_accepted=False)