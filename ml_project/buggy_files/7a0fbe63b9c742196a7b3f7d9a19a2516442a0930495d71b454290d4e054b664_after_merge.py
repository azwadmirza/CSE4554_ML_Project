    def _super_init(self, log_path):
        logbook.RotatingFileHandler.__init__(
            self,
            filename=log_path,
            level=self.level,
            filter=self.filter,
            delay=True,
            max_size=self._max_size,
            backup_count=self._backup_count,
            bubble=self.bubble,
            format_string=DEBUG_LOG_FORMAT,
        )
        FormatterMixin.__init__(self, DEBUG_LOG_FORMAT)