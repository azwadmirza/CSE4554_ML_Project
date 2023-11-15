    def __init__(self, *args):
        super(WordOccurrenceAccumulator, self).__init__(*args)
        self._occurrences = np.zeros(self._vocab_size, dtype='uint32')
        self._co_occurrences = sps.lil_matrix((self._vocab_size, self._vocab_size), dtype='uint32')

        self._uniq_words = np.zeros((self._vocab_size + 1,), dtype=bool)  # add 1 for none token
        self._counter = Counter()