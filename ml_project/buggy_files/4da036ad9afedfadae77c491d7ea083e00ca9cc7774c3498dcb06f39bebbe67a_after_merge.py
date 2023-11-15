    def _ensure_cached(self):
        if not isinstance(self.array, NumpyIndexingAdapter):
            self.array = NumpyIndexingAdapter(np.asarray(self.array))