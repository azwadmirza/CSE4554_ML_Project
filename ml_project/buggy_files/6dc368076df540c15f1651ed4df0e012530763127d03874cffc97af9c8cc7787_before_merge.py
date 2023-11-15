    def dir_list(self, saltenv='base', prefix=''):
        '''
        List the dirs on the master
        '''
        load = {'saltenv': saltenv,
                'prefix': prefix,
                'cmd': '_dir_list'}
        return self.channel.send(load)