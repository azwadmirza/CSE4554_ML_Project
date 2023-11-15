    def format(self, record):
        """Prettify the log output, annotate with simulation time"""
        if record.args:
            msg = record.msg % record.args
        else:
            msg = record.msg

        msg = str(msg)
        level = record.levelname.ljust(_LEVEL_CHARS)

        return self._format(level, record, msg)