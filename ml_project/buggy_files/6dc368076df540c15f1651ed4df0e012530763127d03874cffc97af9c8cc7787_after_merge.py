    def dir_list(self, saltenv='base', prefix=''):
        '''
        List the dirs on the master
        '''
        load = {'saltenv': saltenv,
                'prefix': prefix,
                'cmd': '_dir_list'}
        return salt.utils.data.decode(self.channel.send(load)) if six.PY2 \
            else self.channel.send(load)