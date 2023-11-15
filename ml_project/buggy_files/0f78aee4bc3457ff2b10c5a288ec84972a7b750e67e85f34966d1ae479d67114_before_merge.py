    def symlink_list(self, saltenv='base', prefix=''):
        '''
        List symlinked files and dirs on the master
        '''
        load = {'saltenv': saltenv,
                'prefix': prefix,
                'cmd': '_symlink_list'}
        return self.channel.send(load)