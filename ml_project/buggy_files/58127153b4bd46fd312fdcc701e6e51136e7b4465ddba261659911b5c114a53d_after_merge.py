    def format(self, record):
        """Prettify the log output, annotate with simulation time"""

        msg = record.getMessage()

        # Need to colour each line in case coloring is applied in the message
        msg = '\n'.join([SimColourLogFormatter.loglevel2colour.get(record.levelno,"%s") % line for line in msg.split('\n')])
        level = (SimColourLogFormatter.loglevel2colour.get(record.levelno, "%s") %
                 record.levelname.ljust(_LEVEL_CHARS))

        return self._format(level, record, msg, coloured=True)