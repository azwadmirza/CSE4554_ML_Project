    def daemonize_if_required(self):
        if self.options.daemon:
            if self._setup_mp_logging_listener_ is True:
                # Stop the logging queue listener for the current process
                # We'll restart it once forked
                log.shutdown_multiprocessing_logging_listener(daemonizing=True)

            # Late import so logging works correctly
            salt.utils.daemonize()

        # Setup the multiprocessing log queue listener if enabled
        self._setup_mp_logging_listener()