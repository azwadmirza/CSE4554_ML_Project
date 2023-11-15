    def init_ngrams(self):
        """
        Computes ngrams of all words present in vocabulary and stores vectors for only those ngrams.
        Vectors for other ngrams are initialized with a random uniform distribution in FastText. These
        vectors are discarded here to save space.

        """
        self.wv.ngrams = {}
        all_ngrams = []
        self.wv.syn0 = np.zeros((len(self.wv.vocab), self.vector_size), dtype=REAL)

        for w, vocab in self.wv.vocab.items():
            all_ngrams += self.compute_ngrams(w, self.wv.min_n, self.wv.max_n)
            self.wv.syn0[vocab.index] += np.array(self.wv.syn0_all[vocab.index])

        all_ngrams = set(all_ngrams)
        self.num_ngram_vectors = len(all_ngrams)
        ngram_indices = []
        for i, ngram in enumerate(all_ngrams):
            ngram_hash = self.ft_hash(ngram)
            ngram_indices.append(len(self.wv.vocab) + ngram_hash % self.bucket)
            self.wv.ngrams[ngram] = i
        self.wv.syn0_all = self.wv.syn0_all.take(ngram_indices, axis=0)

        ngram_weights = self.wv.syn0_all

        logger.info("loading weights for %s words for fastText model from %s", len(self.wv.vocab), self.file_name)

        for w, vocab in self.wv.vocab.items():
            word_ngrams = self.compute_ngrams(w, self.wv.min_n, self.wv.max_n)
            for word_ngram in word_ngrams:
                self.wv.syn0[vocab.index] += np.array(ngram_weights[self.wv.ngrams[word_ngram]])

            self.wv.syn0[vocab.index] /= (len(word_ngrams) + 1)
        logger.info("loaded %s weight matrix for fastText model from %s", self.wv.syn0.shape, self.file_name)