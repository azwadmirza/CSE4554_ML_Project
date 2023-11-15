    def __call__(self, *args, **kwargs):
        with self.lock:
            if self._ignore_call:
                self.script_thread.start()
                self._ignore_call = False
                return
        self.original_reply(*args, **kwargs)