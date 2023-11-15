    def symlink_list(self, env='base', prefix=''):
        '''
        List symlinked files and dirs on the master
        '''
        load = {'env': env,
                'prefix': prefix,
                'cmd': '_symlink_list'}
        try:
            return self.auth.crypticle.loads(
                self.sreq.send('aes',
                               self.auth.crypticle.dumps(load),
                               3,
                               60)
            )
        except SaltReqTimeoutError:
            return ''