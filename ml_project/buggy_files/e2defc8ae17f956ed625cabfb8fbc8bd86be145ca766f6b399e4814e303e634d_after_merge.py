    def __init__(self, *, cmd, win_id, parent=None):
        super().__init__(parent)
        self._cmd = cmd
        self._win_id = win_id
        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.setInterval(0)
        self._timer.timeout.connect(self._update_completion)
        self._last_cursor_pos = -1
        self._last_text = None
        self._last_completion_func = None
        self._cmd.update_completion.connect(self.schedule_completion_update)