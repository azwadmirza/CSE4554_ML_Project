    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super(Tokenizer, self).__init__(component_config)

        try:
            self.use_cls_token = self.component_config["use_cls_token"]
        except KeyError:
            raise KeyError(
                "No default value for 'use_cls_token' was set. Please, "
                "add it to the default dict of the tokenizer."
            )