    def _finish(self):
        self.done = True
        self._file.write("\n")