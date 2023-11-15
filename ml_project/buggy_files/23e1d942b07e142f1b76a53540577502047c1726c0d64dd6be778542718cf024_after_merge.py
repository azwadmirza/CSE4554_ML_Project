    def file_list(self, env='base', prefix=''):
        '''
        List the files on the master
        '''
        load = {'env': env,
                'prefix': prefix,
                'cmd': '_file_list'}
        try:
            return self._crypted_transfer(load)
        except SaltReqTimeoutError:
            return ''