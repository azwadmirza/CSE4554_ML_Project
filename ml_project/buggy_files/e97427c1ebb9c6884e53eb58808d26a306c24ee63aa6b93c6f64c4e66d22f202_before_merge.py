    def file_list_emptydirs(self, env='base', prefix=''):
        '''
        List the empty dirs on the master
        '''
        load = {'env': env,
                'prefix': prefix,
                'cmd': '_file_list_emptydirs'}
        try:
            return self.auth.crypticle.loads(
                self.sreq.send('aes',
                               self.auth.crypticle.dumps(load),
                               3,
                               60)
            )
        except SaltReqTimeoutError:
            return ''