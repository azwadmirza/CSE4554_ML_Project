    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super(Tokenizer, self).__init__(component_config)

        try:
            self.use_cls_token = self.component_config["use_cls_token"]
        except KeyError:
            warnings.warn(
                "No default value for 'use_cls_token' was set. Please, "
                "add it to the default dict of the tokenizer and set it to 'False'."
            )
            self.use_cls_token = False