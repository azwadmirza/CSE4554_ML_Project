    def add_vocab(self, sentences):
        """Update model parameters with new `sentences`.

        Parameters
        ----------
        sentences : iterable of list of str
            Text corpus to update this model's parameters from.

        Example
        -------
        .. sourcecode:: pycon

            >>> from gensim.test.utils import datapath
            >>> from gensim.models.word2vec import Text8Corpus
            >>> from gensim.models.phrases import Phrases, ENGLISH_CONNECTOR_WORDS
            >>>
            >>> # Train a phrase detector from a text corpus.
            >>> sentences = Text8Corpus(datapath('testcorpus.txt'))
            >>> phrases = Phrases(sentences, connector_words=ENGLISH_CONNECTOR_WORDS)  # train model
            >>> assert len(phrases.vocab) == 37
            >>>
            >>> more_sentences = [
            ...     [u'the', u'mayor', u'of', u'new', u'york', u'was', u'there'],
            ...     [u'machine', u'learning', u'can', u'be', u'new', u'york', u'sometimes'],
            ... ]
            >>>
            >>> phrases.add_vocab(more_sentences)  # add new sentences to model
            >>> assert len(phrases.vocab) == 60

        """
        # Uses a separate vocab to collect the token counts from `sentences`.
        # This consumes more RAM than merging new sentences into `self.vocab`
        # directly, but gives the new sentences a fighting chance to collect
        # sufficient counts, before being pruned out by the (large) accumulated
        # counts collected in previous learn_vocab runs.
        min_reduce, vocab, total_words = self._learn_vocab(
            sentences, max_vocab_size=self.max_vocab_size, delimiter=self.delimiter,
            progress_per=self.progress_per, connector_words=self.connector_words,
        )

        self.corpus_word_count += total_words
        if self.vocab:
            logger.info("merging %i counts into %s", len(vocab), self)
            self.min_reduce = max(self.min_reduce, min_reduce)
            for word, count in vocab.items():
                self.vocab[word] += count
            if len(self.vocab) > self.max_vocab_size:
                utils.prune_vocab(self.vocab, self.min_reduce)
                self.min_reduce += 1
        else:
            # Optimization for a common case: the current vocab is empty, so apply
            # the new vocab directly, no need to double it in memory.
            self.vocab = vocab
        logger.info("merged %s", self)