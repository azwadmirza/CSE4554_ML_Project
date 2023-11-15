    def start(self):
        if self.show_spin:
            self._spinner_thread.start()
        else:
            self.fh.write("...working... ")
            self.fh.flush()