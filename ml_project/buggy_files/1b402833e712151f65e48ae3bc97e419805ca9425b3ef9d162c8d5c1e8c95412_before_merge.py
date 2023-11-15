    def __init__(self, vocab=True, make_doc=True, meta={}, **kwargs):
        """Initialise a Language object.

        vocab (Vocab): A `Vocab` object. If `True`, a vocab is created via
            `Language.Defaults.create_vocab`.
        make_doc (callable): A function that takes text and returns a `Doc`
            object. Usually a `Tokenizer`.
        pipeline (list): A list of annotation processes or IDs of annotation,
            processes, e.g. a `Tagger` object, or `'tagger'`. IDs are looked
            up in `Language.Defaults.factories`.
        disable (list): A list of component names to exclude from the pipeline.
            The disable list has priority over the pipeline list -- if the same
            string occurs in both, the component is not loaded.
        meta (dict): Custom meta data for the Language class. Is written to by
            models to add model meta data.
        RETURNS (Language): The newly constructed object.
        """
        self._meta = dict(meta)
        self._path = None
        if vocab is True:
            factory = self.Defaults.create_vocab
            vocab = factory(self, **meta.get('vocab', {}))
        self.vocab = vocab
        if make_doc is True:
            factory = self.Defaults.create_tokenizer
            make_doc = factory(self, **meta.get('tokenizer', {}))
        self.tokenizer = make_doc
        self.pipeline = []
        self._optimizer = None