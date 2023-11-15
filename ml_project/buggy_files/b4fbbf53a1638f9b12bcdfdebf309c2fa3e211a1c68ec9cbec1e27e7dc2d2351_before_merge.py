    def find_file(self, path, saltenv, back=None):
        '''
        Find the path and return the fnd structure, this structure is passed
        to other backend interfaces.
        '''
        path = salt.utils.locales.sdecode(path)
        saltenv = salt.utils.locales.sdecode(saltenv)
        back = self.backends(back)
        kwargs = {}
        fnd = {'path': '',
               'rel': ''}
        if os.path.isabs(path):
            return fnd
        if '../' in path:
            return fnd
        if salt.utils.url.is_escaped(path):
            # don't attempt to find URL query arguements in the path
            path = salt.utils.url.unescape(path)
        else:
            if '?' in path:
                hcomps = path.split('?')
                path = hcomps[0]
                comps = hcomps[1].split('&')
                for comp in comps:
                    if '=' not in comp:
                        # Invalid option, skip it
                        continue
                    args = comp.split('=', 1)
                    kwargs[args[0]] = args[1]

        if 'env' in kwargs:
            # "env" is not supported; Use "saltenv".
            kwargs.pop('env')
        if 'saltenv' in kwargs:
            saltenv = kwargs.pop('saltenv')

        if not isinstance(saltenv, six.string_types):
            saltenv = six.text_type(saltenv)

        for fsb in back:
            fstr = '{0}.find_file'.format(fsb)
            if fstr in self.servers:
                fnd = self.servers[fstr](path, saltenv, **kwargs)
                if fnd.get('path'):
                    fnd['back'] = fsb
                    return fnd
        return fnd