    def _ensure_copied(self):
        if not self._copied:
            self.array = np.array(self.array)
            self._copied = True