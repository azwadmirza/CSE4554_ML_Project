    def start(self):
        '''
        Start the actual proxy minion.

        If sub-classed, don't **ever** forget to run:

            super(YourSubClass, self).start()

        NOTE: Run any required code before calling `super()`.
        '''
        super(ProxyMinion, self).start()
        try:
            if check_user(self.config['user']):
                logger.info('The proxy minion is starting up')
                self.minion.tune_in()
        except (KeyboardInterrupt, SaltSystemExit) as exc:
            logger.warn('Stopping the Salt Proxy Minion')
            if isinstance(exc, KeyboardInterrupt):
                logger.warn('Exiting on Ctrl-c')
                self.shutdown()
            else:
                logger.error(str(exc))
                self.shutdown(exc.code)