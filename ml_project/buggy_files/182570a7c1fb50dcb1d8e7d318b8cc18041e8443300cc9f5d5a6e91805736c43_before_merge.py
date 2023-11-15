    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super().__init__(component_config)

        self.model_url = self.component_config.get("model_url", TF_HUB_MODULE_URL)

        self.module = train_utils.load_tf_hub_model(self.model_url)

        self.tokenize_signature = self.module.signatures["tokenize"]