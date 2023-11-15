    def allow_sending_in_thread(value, info=None):
        """ Setter for `_allow_sending` variable.

        It allows or disallows Sentry to send events in the current thread.
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
        SentryReporter._logger.info(f"Allow sending in thread: {value}. Info: {info}")
        SentryReporter._allow_sending_in_thread.set(value)