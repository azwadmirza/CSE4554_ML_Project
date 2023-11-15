    def master_opts(self):
        '''
        Return the master opts data
        '''
        load = {'cmd': '_master_opts'}
        try:
            return self._crypted_transfer(load)
        except SaltReqTimeoutError:
            return ''