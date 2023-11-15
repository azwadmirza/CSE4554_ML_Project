    def file_list_emptydirs(self, saltenv='base', prefix=''):
        '''
        List the empty dirs on the master
        '''
        load = {'saltenv': saltenv,
                'prefix': prefix,
                'cmd': '_file_list_emptydirs'}
        self.channel.send(load)