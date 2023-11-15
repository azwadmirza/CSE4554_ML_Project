    def file_list(self, saltenv='base', prefix='', env=None):
        '''
        List the files on the master
        '''
        if env is not None:
            salt.utils.warn_until(
                'Boron',
                'Passing a salt environment should be done using \'saltenv\' '
                'not \'env\'. This functionality will be removed in Salt '
                'Boron.'
            )
            # Backwards compatibility
            saltenv = env

        load = {'saltenv': saltenv,
                'prefix': prefix,
                'cmd': '_file_list'}

        return self.channel.send(load)