    def format(self, record):
        """Prettify the log output, annotate with simulation time"""

        if record.args:
            msg = record.msg % record.args
        else:
            msg = record.msg

        # Need to colour each line in case coloring is applied in the message
        msg = '\n'.join([SimColourLogFormatter.loglevel2colour[record.levelno] % line for line in msg.split('\n')])
        level = (SimColourLogFormatter.loglevel2colour[record.levelno] %
                 record.levelname.ljust(_LEVEL_CHARS))

        return self._format(level, record, msg, coloured=True)