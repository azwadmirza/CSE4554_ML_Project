    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        skip_model_load: bool = False,
    ) -> None:
        super(HFTransformersNLP, self).__init__(component_config)

        self._load_model_metadata()
        self._load_model_instance(skip_model_load)
        self.whitespace_tokenizer = WhitespaceTokenizer()