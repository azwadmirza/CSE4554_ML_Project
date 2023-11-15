    def handle_exception(self, msg, exc):
        if isinstance(exc, SaltCloudException):
            # It's a know exception an we know own to handle it
            if isinstance(exc, SaltCloudSystemExit):
                # This is a salt cloud system exit
                if exc.exit_code > 0:
                    # the exit code is bigger than 0, it's an error
                    msg = 'Error: {0}'.format(msg)
                self.exit(
                    exc.exit_code,
                    '{0}\n'.format(
                        msg.format(str(exc).rstrip())
                    )
                )
            # It's not a system exit but it's an error we can
            # handle
            self.error(
                msg.format(str(exc))
            )
        # This is a generic exception, log it, include traceback if
        # debug logging is enabled and exit.
        log.error(
            msg.format(exc),
            # Show the traceback if the debug logging level is
            # enabled
            exc_info_on_loglevel=logging.DEBUG
        )
        self.exit(salt.defaults.exitcodes.EX_GENERIC)