    def start(self):
        if not self._active:
            self._active = True
            register_postfork_function(self.thread.start)