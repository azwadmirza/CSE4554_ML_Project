    def __init__(
            self, sentences=None, min_count=5, threshold=10.0,
            max_vocab_size=40000000, delimiter='_', progress_per=10000,
            scoring='default', connector_words=frozenset(),
        ):
        """

        Parameters
        ----------
        sentences : iterable of list of str, optional
            The `sentences` iterable can be simply a list, but for larger corpora, consider a generator that streams
            the sentences directly from disk/network, See :class:`~gensim.models.word2vec.BrownCorpus`,
            :class:`~gensim.models.word2vec.Text8Corpus` or :class:`~gensim.models.word2vec.LineSentence`
            for such examples.
        min_count : float, optional
            Ignore all words and bigrams with total collected count lower than this value.
        threshold : float, optional
            Represent a score threshold for forming the phrases (higher means fewer phrases).
            A phrase of words `a` followed by `b` is accepted if the score of the phrase is greater than threshold.
            Heavily depends on concrete scoring-function, see the `scoring` parameter.
        max_vocab_size : int, optional
            Maximum size (number of tokens) of the vocabulary. Used to control pruning of less common words,
            to keep memory under control. The default of 40M needs about 3.6GB of RAM. Increase/decrease
            `max_vocab_size` depending on how much available memory you have.
        delimiter : str, optional
            Glue character used to join collocation tokens.
        scoring : {'default', 'npmi', function}, optional
            Specify how potential phrases are scored. `scoring` can be set with either a string that refers to a
            built-in scoring function, or with a function with the expected parameter names.
            Two built-in scoring functions are available by setting `scoring` to a string:

            #. "default" - :func:`~gensim.models.phrases.original_scorer`.
            #. "npmi" - :func:`~gensim.models.phrases.npmi_scorer`.
        connector_words : set of str, optional
            Set of words that may be included within a phrase, without affecting its scoring.
            No phrase can start nor end with a connector word; a phrase may contain any number of
            connector words in the middle.

            **If your texts are in English, set** ``connector_words=phrases.ENGLISH_CONNECTOR_WORDS``.

            This will cause phrases to include common English articles, prepositions and
            conjuctions, such as `bank_of_america` or `eye_of_the_beholder`.

            For other languages or specific applications domains, use custom ``connector_words``
            that make sense there: ``connector_words=frozenset("der die das".split())`` etc.

        Examples
        --------
        .. sourcecode:: pycon

            >>> from gensim.test.utils import datapath
            >>> from gensim.models.word2vec import Text8Corpus
            >>> from gensim.models.phrases import Phrases, ENGLISH_CONNECTOR_WORDS
            >>>
            >>> # Load corpus and train a model.
            >>> sentences = Text8Corpus(datapath('testcorpus.txt'))
            >>> phrases = Phrases(sentences, min_count=1, threshold=1, connector_words=ENGLISH_CONNECTOR_WORDS)
            >>>
            >>> # Use the model to detect phrases in a new sentence.
            >>> sent = [u'trees', u'graph', u'minors']
            >>> print(phrases[sent])
            [u'trees_graph', u'minors']
            >>>
            >>> # Or transform multiple sentences at once.
            >>> sents = [[u'trees', u'graph', u'minors'], [u'graph', u'minors']]
            >>> for phrase in phrases[sents]:
            ...     print(phrase)
            [u'trees_graph', u'minors']
            [u'graph_minors']
            >>>
            >>> # Export a FrozenPhrases object that is more efficient but doesn't allow any more training.
            >>> frozen_phrases = phrases.freeze()
            >>> print(frozen_phrases[sent])
            [u'trees_graph', u'minors']

        Notes
        -----

        The ``scoring="npmi"`` is more robust when dealing with common words that form part of common bigrams, and
        ranges from -1 to 1, but is slower to calculate than the default ``scoring="default"``.
        The default is the PMI-like scoring as described in `Mikolov, et. al: "Distributed
        Representations of Words and Phrases and their Compositionality" <https://arxiv.org/abs/1310.4546>`_.

        To use your own custom ``scoring`` function, pass in a function with the following signature:

        * ``worda_count`` - number of corpus occurrences in `sentences` of the first token in the bigram being scored
        * ``wordb_count`` - number of corpus occurrences in `sentences` of the second token in the bigram being scored
        * ``bigram_count`` - number of occurrences in `sentences` of the whole bigram
        * ``len_vocab`` - the number of unique tokens in `sentences`
        * ``min_count`` - the `min_count` setting of the Phrases class
        * ``corpus_word_count`` - the total number of tokens (non-unique) in `sentences`

        The scoring function must accept all these parameters, even if it doesn't use them in its scoring.

        The scoring function **must be pickleable**.

        """
        super().__init__(connector_words=connector_words)
        if min_count <= 0:
            raise ValueError("min_count should be at least 1")

        if threshold <= 0 and scoring == 'default':
            raise ValueError("threshold should be positive for default scoring")
        if scoring == 'npmi' and (threshold < -1 or threshold > 1):
            raise ValueError("threshold should be between -1 and 1 for npmi scoring")

        # Set scoring based on string.
        # Intentially override the value of the scoring parameter rather than set self.scoring here,
        # to still run the check of scoring function parameters in the next code block.
        if isinstance(scoring, str):
            if scoring == 'default':
                scoring = original_scorer
            elif scoring == 'npmi':
                scoring = npmi_scorer
            else:
                raise ValueError(f'unknown scoring method string {scoring} specified')

        scoring_params = [
            'worda_count', 'wordb_count', 'bigram_count', 'len_vocab', 'min_count', 'corpus_word_count',
        ]
        if callable(scoring):
            missing = [param for param in scoring_params if param not in getargspec(scoring)[0]]
            if not missing:
                self.scoring = scoring
            else:
                raise ValueError(f'scoring function missing expected parameters {missing}')

        self.min_count = min_count
        self.threshold = threshold
        self.max_vocab_size = max_vocab_size
        self.vocab = {}  # mapping between token => its count
        self.min_reduce = 1  # ignore any tokens with count smaller than this
        self.delimiter = delimiter
        self.progress_per = progress_per
        self.corpus_word_count = 0

        # Ensure picklability of the scorer.
        try:
            pickle.loads(pickle.dumps(self.scoring))
        except pickle.PickleError:
            raise pickle.PickleError(f'Custom scoring function in {self.__class__.__name__} must be pickle-able')

        if sentences is not None:
            self.add_vocab(sentences)