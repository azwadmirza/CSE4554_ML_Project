    def run(self):
        '''
        Load and start all available api modules
        '''
        if not len(self.netapi):
            logger.error("Did not find any netapi configurations, nothing to start")

        for fun in self.netapi:
            if fun.endswith('.start'):
                logger.info('Starting {0} netapi module'.format(fun))
                self.process_manager.add_process(self.netapi[fun])

        self.process_manager.run()