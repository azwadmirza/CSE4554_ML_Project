    def file_hash(self, load):
        '''
        Return the hash of a given file
        '''
        if 'env' in load:
            salt.utils.warn_until(
                'Boron',
                'Passing a salt environment should be done using \'saltenv\' '
                'not \'env\'. This functionality will be removed in Salt '
                'Boron.'
            )
            load['saltenv'] = load.pop('env')

        if 'path' not in load or 'saltenv' not in load:
            return ''
        if not isinstance(load['saltenv'], six.string_types):
            load['saltenv'] = six.text_type(load['saltenv'])

        fnd = self.find_file(salt.utils.locales.sdecode(load['path']),
                load['saltenv'])
        if not fnd.get('back'):
            return ''
        fstr = '{0}.file_hash'.format(fnd['back'])
        if fstr in self.servers:
            return self.servers[fstr](load, fnd)
        return ''