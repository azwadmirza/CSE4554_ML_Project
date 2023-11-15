    def start(self):
        '''
        Start the actual master.

        If sub-classed, don't **ever** forget to run:

            super(YourSubClass, self).start()

        NOTE: Run any required code before calling `super()`.
        '''
        super(Master, self).start()
        if check_user(self.config['user']):
            logger.info('The salt master is starting up')
            self.master.start()