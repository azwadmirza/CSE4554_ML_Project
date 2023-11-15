    def symlink_list(self, saltenv='base', prefix=''):
        '''
        List symlinked files and dirs on the master
        '''
        load = {'saltenv': saltenv,
                'prefix': prefix,
                'cmd': '_symlink_list'}
        return salt.utils.data.decode(self.channel.send(load)) if six.PY2 \
            else self.channel.send(load)