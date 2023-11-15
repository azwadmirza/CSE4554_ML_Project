    def list_env(self, env='base'):
        '''
        Return a list of the files in the file server's specified environment
        '''
        load = {'env': env,
                'cmd': '_file_list'}
        try:
            return self._crypted_transfer(load)
        except SaltReqTimeoutError:
            return ''