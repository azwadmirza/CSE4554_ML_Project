    def _load_states(self):
        '''
        Read the state loader value and loadup the correct states subsystem
        '''
        if self.states_loader == 'thorium':
            self.states = salt.loader.thorium(self.opts, self.functions, {})  # TODO: Add runners
        else:
            self.states = salt.loader.states(self.opts, self.functions, self.utils,
                                             self.serializers, proxy=self.proxy)