    def __init__(self, enable_spin=True):
        self._stop_running = Event()
        self._spinner_thread = Thread(target=self._start_spinning)
        self._indicator_length = len(next(self.spinner_cycle)) + 1
        self.fh = sys.stdout
        self.show_spin = enable_spin and hasattr(self.fh, "isatty") and self.fh.isatty()