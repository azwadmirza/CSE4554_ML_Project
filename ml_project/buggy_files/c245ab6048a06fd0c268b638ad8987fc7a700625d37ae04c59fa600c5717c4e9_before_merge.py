    def envs(self):
        '''
        Return a list of available environments
        '''
        load = {'cmd': '_file_envs'}
        return self.channel.send(load)