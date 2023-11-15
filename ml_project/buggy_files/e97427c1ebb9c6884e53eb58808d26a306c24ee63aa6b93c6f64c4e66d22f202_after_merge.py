    def file_list_emptydirs(self, env='base', prefix=''):
        '''
        List the empty dirs on the master
        '''
        load = {'env': env,
                'prefix': prefix,
                'cmd': '_file_list_emptydirs'}
        try:
            self._crypted_transfer(load)
        except SaltReqTimeoutError:
            return ''