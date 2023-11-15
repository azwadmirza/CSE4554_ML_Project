    def master_opts(self):
        '''
        Return the master opts data
        '''
        load = {'cmd': '_master_opts'}
        return salt.utils.data.decode(self.channel.send(load)) if six.PY2 \
            else self.channel.send(load)