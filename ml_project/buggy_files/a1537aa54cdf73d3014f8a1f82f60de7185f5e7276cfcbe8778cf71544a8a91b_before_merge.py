    def __init__(self, login, media_players=None) -> None:
        # pylint: disable=unexpected-keyword-arg
        """Initialize the Alexa device."""
        from alexapy import AlexaAPI

        # Class info
        self._login = login
        self.alexa_api = AlexaAPI(self, login)
        self.alexa_api_session = login.session
        self.email = login.email
        self.account = hide_email(login.email)

        # Guard info
        self._appliance_id = None
        self._guard_entity_id = None
        self._friendly_name = "Alexa Guard"
        self._state = None
        self._should_poll = False
        self._attrs: Dict[Text, Text] = {}
        self._media_players = {} or media_players