    def init_ngrams(self):
        """
        Computes ngrams of all words present in vocabulary and stores vectors for only those ngrams.
        Vectors for other ngrams are initialized with a random uniform distribution in FastText. These
        vectors are discarded here to save space.

        """
        self.wv.ngrams = {}
        all_ngrams = []
        for w, v in self.wv.vocab.items():
            all_ngrams += self.compute_ngrams(w, self.wv.min_n, self.wv.max_n)
        all_ngrams = set(all_ngrams)
        self.num_ngram_vectors = len(all_ngrams)
        ngram_indices = []
        for i, ngram in enumerate(all_ngrams):
            ngram_hash = self.ft_hash(ngram)
            ngram_indices.append(len(self.wv.vocab) + ngram_hash % self.bucket)
            self.wv.ngrams[ngram] = i
        self.wv.syn0_all = self.wv.syn0_all.take(ngram_indices, axis=0)