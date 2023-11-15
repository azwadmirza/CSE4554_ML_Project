    def _finish(self):
        self._file.write("]\n")
        self._file.flush()