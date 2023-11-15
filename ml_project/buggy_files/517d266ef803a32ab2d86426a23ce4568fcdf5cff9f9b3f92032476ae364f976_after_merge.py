    def __init__(self, cls, nlp=None):
        self.vocab = nlp.vocab if nlp is not None else cls.create_vocab(nlp)

        MeCab = try_mecab_import()
        self.tokenizer = MeCab.Tagger()
        self.tokenizer.parseToNode('')  # see #2901