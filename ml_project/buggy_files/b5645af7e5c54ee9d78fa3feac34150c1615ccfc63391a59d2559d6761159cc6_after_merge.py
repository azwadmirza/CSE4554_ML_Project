    def __init__(self, login, hass):
        # pylint: disable=unexpected-keyword-arg
        """Initialize the Alexa device."""
        from alexapy import AlexaAPI
        # Class info
        self._login = login
        self.alexa_api = AlexaAPI(self, login)
        self.alexa_api_session = login.session
        self.account = hide_email(login.email)
        self.hass = hass

        # Guard info
        self._appliance_id = None
        self._guard_entity_id = None
        self._friendly_name = "Alexa Guard"
        self._state = None
        self._should_poll = False
        self._attrs = {}

        data = self.alexa_api.get_guard_details(self._login)
        try:
            guard_dict = (data['locationDetails']
                          ['locationDetails']['Default_Location']
                          ['amazonBridgeDetails']['amazonBridgeDetails']
                          ['LambdaBridge_AAA/OnGuardSmartHomeBridgeService']
                          ['applianceDetails']['applianceDetails'])
        except (KeyError, TypeError):
            guard_dict = {}
        for key, value in guard_dict.items():
            if value['modelName'] == "REDROCK_GUARD_PANEL":
                self._appliance_id = value['applianceId']
                self._guard_entity_id = value['entityId']
                self._friendly_name += " " + self._appliance_id[-5:]
                _LOGGER.debug("%s: Discovered %s: %s %s",
                              self.account,
                              self._friendly_name,
                              self._appliance_id,
                              self._guard_entity_id)
        if not self._appliance_id:
            _LOGGER.debug("%s: No Alexa Guard entity found", self.account)
            return None
        # Register event handler on bus
        hass.bus.listen(('{}_{}'.format(ALEXA_DOMAIN,
                                        hide_email(login.email)))[0:32],
                        self._handle_event)
        self.refresh(no_throttle=True)