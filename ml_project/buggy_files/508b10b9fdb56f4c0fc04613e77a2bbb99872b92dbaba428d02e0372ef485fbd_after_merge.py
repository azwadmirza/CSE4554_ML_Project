    def __enter__(self):
        """Set SentryReporter.allow_sending(value)
        """
        self._logger.debug('Enter')
        self._saved_state = self._reporter.get_allow_sending()

        self._reporter.allow_sending_in_thread(self._value, 'AllowSentryReports.__enter__()')
        return self._reporter