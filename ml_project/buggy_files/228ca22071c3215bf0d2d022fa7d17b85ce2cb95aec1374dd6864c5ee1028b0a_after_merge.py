    def __init__(self, value=True, description='', reporter=None):
        """ Initialising a value and a reporter

        Args:
            value: Value that will be used for passing in
                `SentryReporter.allow_sending`.
            description: Will be used while logging.
            reporter: Instance of a reporter. This argument mostly use for
                testing purposes.
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug(f'Value: {value}, description: {description}')

        self._value = value
        self._saved_state = None
        self._reporter = reporter or SentryReporter()