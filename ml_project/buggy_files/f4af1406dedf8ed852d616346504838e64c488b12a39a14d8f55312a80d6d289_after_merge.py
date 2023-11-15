    def format(self, record):
        """Prettify the log output, annotate with simulation time"""

        msg = record.getMessage()
        level = record.levelname.ljust(_LEVEL_CHARS)

        return self._format(level, record, msg)