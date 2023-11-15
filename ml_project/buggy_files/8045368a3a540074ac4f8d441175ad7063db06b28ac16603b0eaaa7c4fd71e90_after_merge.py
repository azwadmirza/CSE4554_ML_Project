    def allow_sending_globally(value, info=None):
        """ Setter for `_allow_sending_global` variable.

        It globally allows or disallows Sentry to send events.
        If `_allow_sending_in_thread` is not set, then `_allow_sending_global`
        will be used.

        Args:
            value: Bool
            info: String that will be used as an indicator of allowing or
            disallowing reason (or the place from which this method has been
            invoked).

        Returns:
            None
        """
        SentryReporter._logger.debug(f"Allow sending globally: {value}. Info: {info}")
        SentryReporter._allow_sending_global = value