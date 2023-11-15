    def file_list(self, saltenv='base', prefix=''):
        '''
        List the files on the master
        '''
        load = {'saltenv': saltenv,
                'prefix': prefix,
                'cmd': '_file_list'}

        return [sdecode(fn_) for fn_ in self.channel.send(load)]