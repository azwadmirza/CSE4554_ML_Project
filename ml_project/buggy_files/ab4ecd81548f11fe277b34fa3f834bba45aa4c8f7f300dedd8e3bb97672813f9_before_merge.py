    def file_list(self, load):
        '''
        Return a list of files from the dominant environment
        '''
        if 'env' in load:
            salt.utils.warn_until(
                'Boron',
                'Passing a salt environment should be done using \'saltenv\' '
                'not \'env\'. This functionality will be removed in Salt '
                'Boron.'
            )
            load['saltenv'] = load.pop('env')

        ret = set()
        if 'saltenv' not in load:
            return []
        for fsb in self._gen_back(load.pop('fsbackend', None)):
            fstr = '{0}.file_list'.format(fsb)
            if fstr in self.servers:
                ret.update(self.servers[fstr](load))
        # upgrade all set elements to a common encoding
        ret = [salt.utils.locales.sdecode(f) for f in ret]
        # some *fs do not handle prefix. Ensure it is filtered
        prefix = load.get('prefix', '').strip('/')
        if prefix != '':
            ret = [f for f in ret if f.startswith(prefix)]
        return sorted(ret)