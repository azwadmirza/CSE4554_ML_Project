    def __init__(self, message, enabled=True, json=False):
        self.message = message
        self.enabled = enabled
        self.json = json

        self._stop_running = Event()
        self._spinner_thread = Thread(target=self._start_spinning)
        self._indicator_length = len(next(self.spinner_cycle)) + 1
        self.fh = sys.stdout
        self.show_spin = enabled and not json and hasattr(self.fh, "isatty") and self.fh.isatty()