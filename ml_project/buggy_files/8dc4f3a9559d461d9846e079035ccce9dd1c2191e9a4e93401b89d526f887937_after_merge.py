    def load_dynamic(self, matches):
        '''
        If autoload_dynamic_modules is True then automatically load the
        dynamic modules
        '''
        if not self.opts['autoload_dynamic_modules']:
            return
        syncd = self.state.functions['saltutil.sync_all'](list(matches))
        if syncd['grains']:
            self.opts['grains'] = salt.loader.grains(self.opts)
            self.state.opts['pillar'] = self.state._gather_pillar()
        self.state.module_refresh()