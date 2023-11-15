    def from_bytes(self, bytes_data, disable=[]):
        """Load state from a binary string.

        bytes_data (bytes): The data to load from.
        disable (list): Names of the pipeline components to disable.
        RETURNS (Language): The `Language` object.
        """
        deserializers = OrderedDict((
            ('vocab', lambda b: self.vocab.from_bytes(b)),
            ('tokenizer', lambda b: self.tokenizer.from_bytes(b, vocab=False)),
            ('meta', lambda b: self.meta.update(ujson.loads(b)))
        ))
        for i, (name, proc) in enumerate(self.pipeline):
            if name in disable:
                continue
            if not hasattr(proc, 'from_bytes'):
                continue
            deserializers[i] = lambda b, proc=proc: proc.from_bytes(b, vocab=False)
        msg = util.from_bytes(bytes_data, deserializers, {})
        return self