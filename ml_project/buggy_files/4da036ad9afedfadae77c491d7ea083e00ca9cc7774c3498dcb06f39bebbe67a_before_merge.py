    def _ensure_cached(self):
        if not isinstance(self.array, np.ndarray):
            self.array = np.asarray(self.array)