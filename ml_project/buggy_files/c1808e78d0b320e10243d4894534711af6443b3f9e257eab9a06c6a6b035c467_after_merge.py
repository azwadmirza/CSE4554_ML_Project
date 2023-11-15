    def __init__(
        self,
        log_dir: Optional[str] = None,
        level=logbook.DEBUG,
        filter=None,
        bubble=True,
        max_size=10 * 1024 * 1024,  # 10 mb
        backup_count=5,
    ) -> None:
        self.disabled = False
        self._msg_buffer: Optional[List[logbook.LogRecord]] = []
        # if we get 1k messages without a logfile being set, something is wrong
        self._bufmax = 1000
        self._log_path = None
        # we need the base handler class' __init__ to run so handling works
        logbook.Handler.__init__(self, level, filter, bubble)
        if log_dir is not None:
            self.set_path(log_dir)
        self._text_format_string = None
        self._max_size = max_size
        self._backup_count = backup_count