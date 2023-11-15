    def start(self):
        try:
            if not self.enabled:
                return
            installed, path = check_if_kite_installed()
            if not installed:
                return
            logger.debug('Kite was found on the system: {0}'.format(path))
            running = check_if_kite_running()
            if running:
                return
            logger.debug('Starting Kite service...')
            self.kite_process = run_program(path)
        finally:
            # Always start client to support possibly undetected Kite builds
            self.client.start()