    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super(Featurizer, self).__init__(component_config)

        try:
            self.return_sequence = self.component_config["return_sequence"]
        except KeyError:
            warnings.warn(
                "No default value for 'return_sequence' was set. Please, "
                "add it to the default dict of the featurizer and set it to 'False'."
            )
            self.return_sequence = False