    def __file_hash_and_stat(self, load):
        '''
        Common code for hashing and stating files
        '''
        if 'env' in load:
            # "env" is not supported; Use "saltenv".
            load.pop('env')

        if 'path' not in load or 'saltenv' not in load:
            return '', None
        if not isinstance(load['saltenv'], six.string_types):
            load['saltenv'] = six.text_type(load['saltenv'])

        fnd = self.find_file(salt.utils.stringutils.to_unicode(load['path']),
                load['saltenv'])
        if not fnd.get('back'):
            return '', None
        stat_result = fnd.get('stat', None)
        fstr = '{0}.file_hash'.format(fnd['back'])
        if fstr in self.servers:
            return self.servers[fstr](load, fnd), stat_result
        return '', None