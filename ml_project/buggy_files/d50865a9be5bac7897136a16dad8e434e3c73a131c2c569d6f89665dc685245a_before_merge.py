    def analyze_text(self, window, doc_num=None):
        self._slide_window(window, doc_num)
        if self._mask.any():
            self._occurrences[self._mask] += 1
            self._counter.update(itertools.combinations(np.nonzero(self._mask)[0], 2))