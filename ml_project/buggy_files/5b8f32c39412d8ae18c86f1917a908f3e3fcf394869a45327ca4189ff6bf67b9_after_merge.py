    def from_disk(self, path, disable=tuple()):
        """Loads state from a directory. Modifies the object in place and
        returns it. If the saved `Language` object contains a model, the
        model will be loaded.

        path (unicode or Path): A path to a directory. Paths may be either
            strings or `Path`-like objects.
        disable (list): Names of the pipeline components to disable.
        RETURNS (Language): The modified `Language` object.

        EXAMPLE:
            >>> from spacy.language import Language
            >>> nlp = Language().from_disk('/path/to/models')
        """
        path = util.ensure_path(path)
        deserializers = OrderedDict((
            ('vocab', lambda p: self.vocab.from_disk(p)),
            ('tokenizer', lambda p: self.tokenizer.from_disk(p, vocab=False)),
            ('meta.json', lambda p: self.meta.update(util.read_json(p)))
        ))
        _fix_pretrained_vectors_name(self)
        for name, proc in self.pipeline:
            if name in disable:
                continue
            if not hasattr(proc, 'to_disk'):
                continue
            deserializers[name] = lambda p, proc=proc: proc.from_disk(p, vocab=False)
        exclude = {p: False for p in disable}
        if not (path / 'vocab').exists():
            exclude['vocab'] = True
        util.from_disk(path, deserializers, exclude)
        self._path = path
        return self