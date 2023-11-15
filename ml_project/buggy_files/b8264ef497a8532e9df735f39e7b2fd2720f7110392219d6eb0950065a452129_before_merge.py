    def __init__(self, model=None, topics=None, texts=None, corpus=None, dictionary=None,
                 window_size=None, coherence='c_v', topn=10, processes=-1):
        """
        Args:
        ----
        model : Pre-trained topic model. Should be provided if topics is not provided.
                Currently supports LdaModel, LdaMallet wrapper and LdaVowpalWabbit wrapper. Use 'topics'
                parameter to plug in an as yet unsupported model.
        topics : List of tokenized topics. If this is preferred over model, dictionary should be provided. eg::
                 topics = [['human', 'machine', 'computer', 'interface'],
                               ['graph', 'trees', 'binary', 'widths']]
        texts : Tokenized texts. Needed for coherence models that use sliding window based probability estimator, eg::
                texts = [['system', 'human', 'system', 'eps'],
                             ['user', 'response', 'time'],
                             ['trees'],
                             ['graph', 'trees'],
                             ['graph', 'minors', 'trees'],
                             ['graph', 'minors', 'survey']]
        corpus : Gensim document corpus.
        dictionary : Gensim dictionary mapping of id word to create corpus. If model.id2word is present,
                     this is not needed. If both are provided, dictionary will be used.
        window_size : Is the size of the window to be used for coherence measures using boolean sliding window as their
                      probability estimator. For 'u_mass' this doesn't matter.
                      If left 'None' the default window sizes are used which are:
                      'c_v' : 110
                      'c_uci' : 10
                      'c_npmi' : 10
        coherence : Coherence measure to be used. Supported values are:
                    'u_mass'
                    'c_v'
                    'c_uci' also popularly known as c_pmi
                    'c_npmi'
                    For 'u_mass' corpus should be provided. If texts is provided, it will be converted
                    to corpus using the dictionary. For 'c_v', 'c_uci' and 'c_npmi' texts should be provided.
                    Corpus is not needed.
        topn : Integer corresponding to the number of top words to be extracted from each topic.
        processes : number of processes to use for probability estimation phase; any value less than 1 will be
                    interpreted to mean num_cpus - 1; default is -1.
        """
        if model is None and topics is None:
            raise ValueError("One of model or topics has to be provided.")
        elif topics is not None and dictionary is None:
            raise ValueError("dictionary has to be provided if topics are to be used.")

        if texts is None and corpus is None:
            raise ValueError("One of texts or corpus has to be provided.")

        # Check if associated dictionary is provided.
        if dictionary is None:
            if isinstance(model.id2word, FakeDict):
                raise ValueError(
                    "The associated dictionary should be provided with the corpus or 'id2word'"
                    " for topic model should be set as the associated dictionary.")
            else:
                self.dictionary = model.id2word
        else:
            self.dictionary = dictionary

        # Check for correct inputs for u_mass coherence measure.
        self.coherence = coherence
        if coherence in boolean_document_based:
            if is_corpus(corpus)[0]:
                self.corpus = corpus
            elif texts is not None:
                self.texts = texts
                self.corpus = [self.dictionary.doc2bow(text) for text in self.texts]
            else:
                raise ValueError(
                    "Either 'corpus' with 'dictionary' or 'texts' should "
                    "be provided for %s coherence.", coherence)

        # Check for correct inputs for c_v coherence measure.
        elif coherence in sliding_window_based:
            self.window_size = window_size
            if self.window_size is None:
                self.window_size = SLIDING_WINDOW_SIZES[self.coherence]
            if texts is None:
                raise ValueError("'texts' should be provided for %s coherence.", coherence)
            else:
                self.texts = texts
        else:
            raise ValueError("%s coherence is not currently supported.", coherence)

        self.topn = topn
        self._model = model
        self._accumulator = None
        self._topics = None
        self.topics = topics

        self.processes = processes if processes > 1 else max(1, mp.cpu_count() - 1)