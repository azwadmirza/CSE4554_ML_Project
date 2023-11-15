    def start(self):
        '''
        Start the actual syndic.

        If sub-classed, don't **ever** forget to run:

            super(YourSubClass, self).start()

        NOTE: Run any required code before calling `super()`.
        '''
        super(Syndic, self).start()
        if check_user(self.config['user']):
            log.info('The salt syndic is starting up')
            try:
                self.syndic.tune_in()
            except KeyboardInterrupt:
                log.warn('Stopping the Salt Syndic Minion')
                self.shutdown()