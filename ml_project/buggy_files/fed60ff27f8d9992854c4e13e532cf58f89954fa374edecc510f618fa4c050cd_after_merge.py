    def __init__(self) -> None:
        """
        Thai named-entity recognizer.
        """
        self.crf = CRFTagger()
        self.crf.open(get_corpus_path(_CORPUS_NAME))