    def load(cls, *args, **kwargs):
        """Load a previously saved :class:`~gensim.models.phrases.Phrases` /
        :class:`~gensim.models.phrases.FrozenPhrases` model.

        Handles backwards compatibility from older versions which did not support pluggable scoring functions.

        Parameters
        ----------
        args : object
            See :class:`~gensim.utils.SaveLoad.load`.
        kwargs : object
            See :class:`~gensim.utils.SaveLoad.load`.

        """
        model = super(_PhrasesTransformation, cls).load(*args, **kwargs)

        # Upgrade FrozenPhrases
        try:
            phrasegrams = getattr(model, "phrasegrams", {})
            component, score = next(iter(phrasegrams.items()))
            if isinstance(score, tuple):
                # Value in phrasegrams used to be a tuple; keep only the 2nd tuple component = score.
                model.phrasegrams = {
                    str(model.delimiter.join(key), encoding='utf8'): val[1]
                    for key, val in phrasegrams.items()
                }
            elif isinstance(component, tuple):  # 3.8 => 4.0: phrasegram keys are strings, not tuples with bytestrings
                model.phrasegrams = {
                    str(model.delimiter.join(component), encoding='utf8'): score
                    for key, val in phrasegrams.items()
                }
        except StopIteration:
            # no phrasegrams, nothing to upgrade
            pass

        # If no scoring parameter, use default scoring.
        if not hasattr(model, 'scoring'):
            logger.warning('older version of %s loaded without scoring function', cls.__name__)
            logger.warning('setting pluggable scoring method to original_scorer for compatibility')
            model.scoring = original_scorer
        # If there is a scoring parameter, and it's a text value, load the proper scoring function.
        if hasattr(model, 'scoring'):
            if isinstance(model.scoring, str):
                if model.scoring == 'default':
                    logger.warning('older version of %s loaded with "default" scoring parameter', cls.__name__)
                    logger.warning('setting scoring method to original_scorer for compatibility')
                    model.scoring = original_scorer
                elif model.scoring == 'npmi':
                    logger.warning('older version of %s loaded with "npmi" scoring parameter', cls.__name__)
                    logger.warning('setting scoring method to npmi_scorer for compatibility')
                    model.scoring = npmi_scorer
                else:
                    raise ValueError(f'failed to load {cls.__name__} model, unknown scoring "{model.scoring}"')

        # common_terms didn't exist pre-3.?, and was renamed to connector in 4.0.0.
        if hasattr(model, "common_terms"):
            model.connector_words = model.common_terms
            del model.common_terms
        else:
            logger.warning(
                'older version of %s loaded without common_terms attribute, setting connector_words to an empty set',
                cls.__name__,
            )
            model.connector_words = frozenset()

        if not hasattr(model, 'corpus_word_count'):
            logger.warning('older version of %s loaded without corpus_word_count', cls.__name__)
            logger.warning('setting corpus_word_count to 0, do not use it in your scoring function')
            model.corpus_word_count = 0

        # Before 4.0.0, we stored strings as UTF8 bytes internally, to save RAM. Since 4.0.0, we use strings.
        if getattr(model, 'vocab', None):
            word = next(iter(model.vocab))  # get a random key – any key will do
            if not isinstance(word, str):
                logger.info("old version of %s loaded, upgrading %i words in memory", cls.__name__, len(model.vocab))
                logger.info("re-save the loaded model to avoid this upgrade in the future")
                vocab = defaultdict(int)
                for key, value in model.vocab.items():  # needs lots of extra RAM temporarily!
                    vocab[str(key, encoding='utf8')] = value
                model.vocab = vocab
        if not isinstance(model.delimiter, str):
            model.delimiter = str(model.delimiter, encoding='utf8')
        return model