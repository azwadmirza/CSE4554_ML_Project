    def _super_init(self, log_path):
        logbook.TimedRotatingFileHandler.__init__(
            self,
            filename=log_path,
            level=self.level,
            filter=self.filter,
            bubble=self.bubble,
            format_string=DEBUG_LOG_FORMAT,
            date_format='%Y-%m-%d',
            backup_count=7,
            timed_filename_for_current=False,
        )
        FormatterMixin.__init__(self, DEBUG_LOG_FORMAT)