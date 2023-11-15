    def serve_file(self, load):
        '''
        Serve up a chunk of a file
        '''
        ret = {'data': '',
               'dest': ''}
        if 'env' in load:
            salt.utils.warn_until(
                'Boron',
                'Passing a salt environment should be done using \'saltenv\' '
                'not \'env\'. This functionality will be removed in Salt '
                'Boron.'
            )
            load['saltenv'] = load.pop('env')

        if 'path' not in load or 'loc' not in load or 'saltenv' not in load:
            return ret
        if not isinstance(load['saltenv'], six.string_types):
            load['saltenv'] = six.text_type(load['saltenv'])

        fnd = self.find_file(load['path'], load['saltenv'])
        if not fnd.get('back'):
            return ret
        fstr = '{0}.serve_file'.format(fnd['back'])
        if fstr in self.servers:
            return self.servers[fstr](load, fnd)
        return ret