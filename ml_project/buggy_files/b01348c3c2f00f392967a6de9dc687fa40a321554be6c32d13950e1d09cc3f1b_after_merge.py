    def init(sentry_url='', scrubber=None):
        """ Initialization.

        This method should be called in each process that uses SentryReporter.

        Args:
            sentry_url: URL for Sentry server. If it is empty then Sentry's
                sending mechanism will not be initialized.

            scrubber: a class that will be used for scrubbing sending events.
                Only a single method should be implemented in the class:
                ```
                    def scrub_event(self, event):
                        pass
                ```
        Returns:
            Sentry Guard.
        """
        SentryReporter._logger.debug(f"Init: {sentry_url}")
        SentryReporter._scrubber = scrubber
        return sentry_sdk.init(
            sentry_url,
            release=None,
            # https://docs.sentry.io/platforms/python/configuration/integrations/
            integrations=[
                LoggingIntegration(
                    level=logging.INFO,  # Capture info and above as breadcrumbs
                    event_level=logging.ERROR,  # Send errors as events
                ),
                ThreadingIntegration(propagate_hub=True),
            ],
            before_send=SentryReporter._before_send,
        )