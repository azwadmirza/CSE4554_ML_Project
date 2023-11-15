    def list_env(self, saltenv='base'):
        '''
        Return a list of the files in the file server's specified environment
        '''
        load = {'saltenv': saltenv,
                'cmd': '_file_list'}
        return self.channel.send(load)