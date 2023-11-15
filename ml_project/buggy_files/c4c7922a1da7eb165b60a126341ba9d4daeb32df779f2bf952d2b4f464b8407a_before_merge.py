    def __prep_mod_opts(self, opts):
        '''
        Strip out of the opts any logger instance
        '''
        if 'grains' in opts:
            self._grains = opts['grains']
        else:
            self._grains = {}
        if 'pillar' in opts:
            self._pillar = opts['pillar']
        else:
            self._pillar = {}

        mod_opts = {}
        for key, val in list(opts.items()):
            if key == 'logger':
                continue
            mod_opts[key] = val
        return mod_opts