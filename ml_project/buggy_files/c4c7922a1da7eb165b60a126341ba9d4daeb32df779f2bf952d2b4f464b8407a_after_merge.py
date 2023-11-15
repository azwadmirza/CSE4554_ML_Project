    def __prep_mod_opts(self, opts):
        '''
        Strip out of the opts any logger instance
        '''
        if '__grains__' not in self.pack:
            self.context_dict['grains'] = opts.get('grains', {})
            self.pack['__grains__'] = salt.utils.context.NamespacedDictWrapper(self.context_dict, 'grains')

        if '__pillar__' not in self.pack:
            self.context_dict['pillar'] = opts.get('pillar', {})
            self.pack['__pillar__'] = salt.utils.context.NamespacedDictWrapper(self.context_dict, 'pillar')

        mod_opts = {}
        for key, val in list(opts.items()):
            if key == 'logger':
                continue
            mod_opts[key] = val
        return mod_opts