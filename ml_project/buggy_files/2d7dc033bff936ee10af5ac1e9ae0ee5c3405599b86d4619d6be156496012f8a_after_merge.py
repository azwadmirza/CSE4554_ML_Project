    def symlink_list(self, env='base', prefix=''):
        '''
        List symlinked files and dirs on the master
        '''
        load = {'env': env,
                'prefix': prefix,
                'cmd': '_symlink_list'}
        try:
            return self._crypted_transfer(load)
        except SaltReqTimeoutError:
            return ''