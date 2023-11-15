    def envs(self):
        '''
        Return a list of available environments
        '''
        load = {'cmd': '_file_envs'}
        return salt.utils.data.decode(self.channel.send(load)) if six.PY2 \
            else self.channel.send(load)