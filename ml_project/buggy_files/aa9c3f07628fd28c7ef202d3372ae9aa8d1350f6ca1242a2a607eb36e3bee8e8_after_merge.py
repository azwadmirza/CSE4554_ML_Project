    def run(self):
        '''
        Load and start all available api modules
        '''
        if not len(self.netapi):
            log.error("Did not find any netapi configurations, nothing to start")

        for fun in self.netapi:
            if fun.endswith('.start'):
                log.info('Starting {0} netapi module'.format(fun))
                self.process_manager.add_process(self.netapi[fun])

        # Install the SIGINT/SIGTERM handlers if not done so far
        if signal.getsignal(signal.SIGINT) is signal.SIG_DFL:
            # No custom signal handling was added, install our own
            signal.signal(signal.SIGINT, self._handle_signals)

        if signal.getsignal(signal.SIGTERM) is signal.SIG_DFL:
            # No custom signal handling was added, install our own
            signal.signal(signal.SIGINT, self._handle_signals)

        self.process_manager.run()