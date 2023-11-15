    def _validate_config(self, conf: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the configuration follow the Config Schema
        :param conf: Config in JSON format
        :return: Returns the config if valid, otherwise throw an exception
        """
        try:
            validate(conf, constants.CONF_SCHEMA, Draft4Validator)
            return conf
        except ValidationError as exception:
            logger.critical(
                'Invalid configuration. See config.json.example. Reason: %s',
                exception
            )
            raise ValidationError(
                best_match(Draft4Validator(constants.CONF_SCHEMA).iter_errors(conf)).message
            )