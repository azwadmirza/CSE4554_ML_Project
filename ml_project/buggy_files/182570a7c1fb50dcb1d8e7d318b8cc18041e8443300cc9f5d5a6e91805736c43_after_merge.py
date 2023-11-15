    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework.

        Args:
            component_config: User configuration for the component
        """
        super().__init__(component_config)

        self.model_url = self._get_validated_model_url()

        self.module = train_utils.load_tf_hub_model(self.model_url)

        self.tokenize_signature = self.module.signatures["tokenize"]