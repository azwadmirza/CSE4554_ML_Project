    def list_env(self, env='base'):
        '''
        Return a list of the files in the file server's specified environment
        '''
        load = {'env': env,
                'cmd': '_file_list'}
        try:
            return self.auth.crypticle.loads(
                self.sreq.send('aes',
                               self.auth.crypticle.dumps(load),
                               3,
                               60)
            )
        except SaltReqTimeoutError:
            return ''