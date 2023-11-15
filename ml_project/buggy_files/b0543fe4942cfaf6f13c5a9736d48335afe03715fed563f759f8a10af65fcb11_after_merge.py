    def file_list_emptydirs(self, load):
        '''
        List all emptydirs in the given environment
        '''
        if 'env' in load:
            # "env" is not supported; Use "saltenv".
            load.pop('env')

        ret = set()
        if 'saltenv' not in load:
            return []
        if not isinstance(load['saltenv'], six.string_types):
            load['saltenv'] = six.text_type(load['saltenv'])

        for fsb in self.backends(None):
            fstr = '{0}.file_list_emptydirs'.format(fsb)
            if fstr in self.servers:
                ret.update(self.servers[fstr](load))
        # some *fs do not handle prefix. Ensure it is filtered
        prefix = load.get('prefix', '').strip('/')
        if prefix != '':
            ret = [f for f in ret if f.startswith(prefix)]
        return sorted(ret)