    def file_list_emptydirs(self, saltenv='base', prefix=''):
        '''
        List the empty dirs on the master
        '''
        load = {'saltenv': saltenv,
                'prefix': prefix,
                'cmd': '_file_list_emptydirs'}
        return salt.utils.data.decode(self.channel.send(load)) if six.PY2 \
            else self.channel.send(load)