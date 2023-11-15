    def file_list(self, saltenv='base', prefix=''):
        '''
        List the files on the master
        '''
        load = {'saltenv': saltenv,
                'prefix': prefix,
                'cmd': '_file_list'}
        return salt.utils.data.decode(self.channel.send(load)) if six.PY2 \
            else self.channel.send(load)