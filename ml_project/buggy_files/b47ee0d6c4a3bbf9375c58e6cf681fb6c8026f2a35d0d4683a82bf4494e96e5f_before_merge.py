    def master_opts(self):
        '''
        Return the master opts data
        '''
        load = {'cmd': '_master_opts'}
        try:
            return self.auth.crypticle.loads(
                self.sreq.send('aes',
                               self.auth.crypticle.dumps(load),
                               3,
                               60)
            )
        except SaltReqTimeoutError:
            return ''