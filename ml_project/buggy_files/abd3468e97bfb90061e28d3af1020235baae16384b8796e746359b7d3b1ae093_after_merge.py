    def __init__(
        self, language: str, treebank: Optional[str] = None, stanza_debug_level="ERROR"
    ) -> None:
        """Constructor for ``get_stanza_models`` wrapper class.

        TODO: Do tests for all langs and available models for each

        >>> stanza_wrapper = StanzaWrapper(language='grc', stanza_debug_level="INFO")
        >>> isinstance(stanza_wrapper, StanzaWrapper)
        True
        >>> stanza_wrapper.language
        'grc'
        >>> stanza_wrapper.treebank
        'proiel'

        >>> stanza_wrapper = StanzaWrapper(language="grc", treebank="perseus", stanza_debug_level="INFO")
        >>> isinstance(stanza_wrapper, StanzaWrapper)
        True
        >>> stanza_wrapper.language
        'grc'
        >>> stanza_wrapper.treebank
        'perseus'
        >>> from cltkv1.languages.example_texts import get_example_text
        >>> stanza_doc = stanza_wrapper.parse(get_example_text("grc"))

        >>> StanzaWrapper(language="xxx", stanza_debug_level="INFO")
        Traceback (most recent call last):
          ...
        cltkv1.core.exceptions.UnknownLanguageError: Language 'xxx' either not in scope for CLTK or not supported by Stanza.

        >>> stanza_wrapper = StanzaWrapper(language="grc", treebank="proiel", stanza_debug_level="INFO")
        >>> stanza_doc = stanza_wrapper.parse(get_example_text("grc"))

        >>> stanza_wrapper = StanzaWrapper(language="lat", treebank="perseus", stanza_debug_level="INFO")
        >>> stanza_doc = stanza_wrapper.parse(get_example_text("lat"))

        >>> stanza_wrapper = StanzaWrapper(language="lat", treebank="proiel", stanza_debug_level="INFO")
        >>> stanza_doc = stanza_wrapper.parse(get_example_text("lat"))

        >>> stanza_wrapper = StanzaWrapper(language="chu", stanza_debug_level="INFO")
        >>> stanza_doc = stanza_wrapper.parse(get_example_text("chu"))

        # >>> stanza_wrapper = StanzaWrapper(language="cop", stanza_debug_level="INFO")
        # >>> stanza_doc = stanza_wrapper.parse(get_example_text("cop"))

        >>> stanza_wrapper = StanzaWrapper(language="lzh", stanza_debug_level="INFO")
        >>> stanza_doc = stanza_wrapper.parse(get_example_text("lzh"))

        >>> stanza_wrapper = StanzaWrapper(language="lat", treebank="xxx", stanza_debug_level="INFO")
        Traceback (most recent call last):
          ...
        cltkv1.core.exceptions.UnimplementedAlgorithmError: Invalid treebank 'xxx' for language 'lat'.
        """
        self.language = language
        self.treebank = treebank
        self.stanza_debug_level = stanza_debug_level

        # Setup language
        self.map_langs_cltk_stanza = {
            "chu": "Old_Church_Slavonic",
            "cop": "Coptic",
            "fro": "Old_French",
            "grc": "Ancient_Greek",
            "got": "Gothic",
            "lat": "Latin",
            "lzh": "Classical_Chinese",
        }

        self.wrapper_available = self.is_wrapper_available()  # type: bool
        if not self.wrapper_available:
            raise UnknownLanguageError(
                "Language '{}' either not in scope for CLTK or not supported by Stanza.".format(
                    self.language
                )
            )
        self.stanza_code = self._get_stanza_code()

        # Setup optional treebank if specified
        # TODO: Write tests for all treebanks
        self.map_code_treebanks = dict(
            grc=["proiel", "perseus"], la=["perseus", "proiel", "ittb"]
        )
        # if not specified, will use the default treebank chosen by stanza
        if self.treebank:
            valid_treebank = self._is_valid_treebank()
            if not valid_treebank:
                raise UnimplementedAlgorithmError(
                    f"Invalid treebank '{self.treebank}' for language '{self.language}'."
                )
        else:
            self.treebank = self._get_default_treebank()

        # check if model present
        # this fp is just to confirm that some model has already been downloaded.
        # TODO: This is a weak check for the models actually being downloaded and valid
        # TODO: Use ``models_dir`` var from below and make self. or global to module
        self.model_path = os.path.expanduser(
            f"~/stanza_resources/{self.stanza_code}/tokenize/{self.treebank}.pt"
        )
        if not self._is_model_present():
            # download model if necessary
            self._download_model()

        # instantiate actual stanza class
        # Note: `suppress_stdout` is used to prevent `stanza`
        # from printing a long log of its parameters to screen.
        # Though we should capture these, within `_load_pipeline()`,
        # for the log file.
        with suppress_stdout():
            self.nlp = self._load_pipeline()