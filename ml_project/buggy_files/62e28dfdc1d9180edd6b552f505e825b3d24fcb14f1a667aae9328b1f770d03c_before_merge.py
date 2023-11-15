    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super().__init__(component_config)

        self.module = train_utils.load_tf_hub_model(TF_HUB_MODULE_URL)

        self.tokenize_signature = self.module.signatures["tokenize"]