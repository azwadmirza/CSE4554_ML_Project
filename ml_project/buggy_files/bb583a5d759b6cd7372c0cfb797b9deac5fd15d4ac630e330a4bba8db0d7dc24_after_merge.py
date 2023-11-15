    def start(self):
        if self.show_spin:
            self._spinner_thread.start()
        elif not self.json:
            self.fh.write("...working... ")
            self.fh.flush()