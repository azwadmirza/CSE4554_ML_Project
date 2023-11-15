    def load(cls, *args, **kwargs):
        """Load a previously saved `FastText` model.

        Parameters
        ----------
        fname : str
            Path to the saved file.

        Returns
        -------
        :class:`~gensim.models.fasttext.FastText`
            Loaded model.

        See Also
        --------
        :meth:`~gensim.models.fasttext.FastText.save`
            Save :class:`~gensim.models.fasttext.FastText` model.

        """
        try:
            model = super(FastText, cls).load(*args, **kwargs)
            if hasattr(model.wv, 'hash2index'):
                gensim.models.keyedvectors._rollback_optimization(model.wv)

            if not hasattr(model.trainables, 'vectors_vocab_lockf') and hasattr(model.wv, 'vectors_vocab'):
                model.trainables.vectors_vocab_lockf = ones(model.wv.vectors_vocab.shape, dtype=REAL)
            if not hasattr(model.trainables, 'vectors_ngrams_lockf') and hasattr(model.wv, 'vectors_ngrams'):
                model.trainables.vectors_ngrams_lockf = ones(model.wv.vectors_ngrams.shape, dtype=REAL)

            if not hasattr(model.wv, 'compatible_hash'):
                logger.warning(
                    "This older model was trained with a buggy hash function. "
                    "The model will continue to work, but consider training it "
                    "from scratch."
                )
                model.wv.compatible_hash = False

            if not hasattr(model.wv, 'bucket'):
                model.wv.bucket = model.trainables.bucket

            return model
        except AttributeError:
            logger.info('Model saved using code from earlier Gensim Version. Re-loading old model in a compatible way.')
            from gensim.models.deprecated.fasttext import load_old_fasttext
            return load_old_fasttext(*args, **kwargs)