    def run(self):
        '''
        Run the master service!
        '''
        if salt.utils.is_windows():
            # Calculate function references since they can't be pickled.
            self.utils = salt.loader.utils(self.opts, proxy=self.proxy)
            if self.opts['__role'] == 'master':
                self.runners = salt.loader.runner(self.opts, utils=self.utils)
            else:
                self.runners = []
            self.funcs = salt.loader.minion_mods(self.opts, utils=self.utils, proxy=self.proxy)

        self.engine = salt.loader.engines(self.opts,
                                          self.funcs,
                                          self.runners,
                                          proxy=self.proxy)
        kwargs = self.config or {}
        try:
            self.engine[self.fun](**kwargs)
        except Exception as exc:
            log.critical('Engine {0} could not be started! Error: {1}'.format(self.engine, exc))