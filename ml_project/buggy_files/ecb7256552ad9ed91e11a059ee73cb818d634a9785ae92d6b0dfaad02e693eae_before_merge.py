    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore SentryReporter.allow_sending(old_value)
        """
        self._logger.info('Exit')
        self._reporter.allow_sending_in_thread(self._saved_state, 'AllowSentryReports.__exit__()')