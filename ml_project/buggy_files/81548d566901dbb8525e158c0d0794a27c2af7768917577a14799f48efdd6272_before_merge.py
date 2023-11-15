    def __init__(self, allow_pickle=True):
        """Main class turn on."""
        self.allow_pickle = allow_pickle
        self.monitors = {}
        self.failed = []
        self.still_failing = []
        self.skipped = []
        self.warning = []
        self.remote_monitors = {}

        self.loggers = {}
        self.alerters = {}

        try:
            signal.signal(signal.SIGHUP, self.hup_loggers)
        except ValueError:  # pragma: no cover
            module_logger.warning("Unable to trap SIGHUP... maybe it doesn't exist on this platform.\n")