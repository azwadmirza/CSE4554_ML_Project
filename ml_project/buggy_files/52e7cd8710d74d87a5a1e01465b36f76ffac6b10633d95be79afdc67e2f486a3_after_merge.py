    def __init__(self, config, opsdroid=None):
        """Create the connector."""
        super().__init__(config, opsdroid=opsdroid)
        _LOGGER.debug(_("Starting Slack connector"))
        self.name = "slack"
        self.default_target = config.get("default-room", "#general")
        self.icon_emoji = config.get("icon-emoji", ":robot_face:")
        self.token = config["api-token"]
        self.timeout = config.get("connect-timeout", 10)
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.slack = slack.WebClient(
            token=self.token, run_async=True, ssl=self.ssl_context
        )
        self.slack_rtm = slack.RTMClient(
            token=self.token, run_async=True, ssl=self.ssl_context
        )
        self.websocket = None
        self.bot_name = config.get("bot-name", "opsdroid")
        self.auth_info = None
        self.user_info = None
        self.bot_id = None
        self.known_users = {}
        self.keepalive = None
        self.reconnecting = False
        self.listening = True
        self._message_id = 0

        # Register callbacks
        slack.RTMClient.on(event="message", callback=self.process_message)