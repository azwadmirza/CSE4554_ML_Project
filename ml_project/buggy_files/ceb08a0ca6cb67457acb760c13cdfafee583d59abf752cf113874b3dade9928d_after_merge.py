    def dir_list(self, env='base', prefix=''):
        '''
        List the dirs on the master
        '''
        load = {'env': env,
                'prefix': prefix,
                'cmd': '_dir_list'}
        try:
            return self._crypted_transfer(load)
        except SaltReqTimeoutError:
            return ''