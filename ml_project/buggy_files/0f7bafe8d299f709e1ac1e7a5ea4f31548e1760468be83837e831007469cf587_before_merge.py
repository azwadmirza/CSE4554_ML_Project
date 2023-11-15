    def call(self, cleanup_protecteds):
        '''
        Start the actual minion as a caller minion.

        cleanup_protecteds is list of yard host addresses that should not be
        cleaned up this is to fix race condition when salt-caller minion starts up

        If sub-classed, don't **ever** forget to run:

            super(YourSubClass, self).start()

        NOTE: Run any required code before calling `super()`.
        '''
        try:
            self.prepare()
            if check_user(self.config['user']):
                self.minion.opts['__role'] = kinds.APPL_KIND_NAMES[kinds.applKinds.caller]
                self.minion.opts['raet_cleanup_protecteds'] = cleanup_protecteds
                self.minion.call_in()
        except (KeyboardInterrupt, SaltSystemExit) as exc:
            logger.warn('Stopping the Salt Minion')
            if isinstance(exc, KeyboardInterrupt):
                logger.warn('Exiting on Ctrl-c')
                self.shutdown()
            else:
                logger.error(str(exc))
                self.shutdown(exc.code)