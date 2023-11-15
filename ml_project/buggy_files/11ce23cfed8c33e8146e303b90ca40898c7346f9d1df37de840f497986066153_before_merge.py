    def __init__(self, config, opsdroid=None):
        """Create the connector.

        Args:
            config (dict): configuration settings from the
                file config.yaml.

        """
        _LOGGER.debug("Loaded telegram connector")
        super().__init__(config, opsdroid=opsdroid)
        self.name = "telegram"
        self.opsdroid = opsdroid
        self.latest_update = None
        self.default_room = None
        self.listening = True
        self.default_user = config.get("default-user", None)
        self.whitelisted_users = config.get("whitelisted-users", None)
        self.update_interval = config.get("update_interval", 1)

        try:
            self.token = config["token"]
        except (KeyError, AttributeError):
            _LOGGER.error("Unable to login: Access token is missing. "
                          "Telegram connector will be unavailable.")