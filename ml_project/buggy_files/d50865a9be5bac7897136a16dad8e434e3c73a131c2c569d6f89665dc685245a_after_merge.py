    def analyze_text(self, window, doc_num=None):
        self._slide_window(window, doc_num)
        mask = self._uniq_words[:-1]  # to exclude none token
        if mask.any():
            self._occurrences[mask] += 1
            self._counter.update(itertools.combinations(np.nonzero(mask)[0], 2))