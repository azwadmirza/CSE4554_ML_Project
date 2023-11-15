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
                log.info('The proxy minion is starting up')
                self.verify_hash_type()
                self.action_log_info('Starting up')
                self.minion.tune_in()
        except (KeyboardInterrupt, SaltSystemExit) as exc:
            self.action_log_info('Stopping')
            if isinstance(exc, KeyboardInterrupt):
                log.warning('Exiting on Ctrl-c')
                self.shutdown()
            else:
                log.error(str(exc))
                self.shutdown(exc.code)