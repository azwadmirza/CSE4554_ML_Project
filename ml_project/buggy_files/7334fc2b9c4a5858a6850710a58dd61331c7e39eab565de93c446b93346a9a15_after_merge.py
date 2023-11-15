def setup_platform(hass, config, add_devices_callback,
                   discovery_info=None):
    """Set up the Alexa alarm control panel platform."""
    devices = []  # type: List[AlexaAlarmControlPanel]
    for account, account_dict in (hass.data[DATA_ALEXAMEDIA]
                                  ['accounts'].items()):
        alexa_client = AlexaAlarmControlPanel(account_dict['login_obj'],
                                              hass)  \
                                              # type: AlexaAlarmControlPanel
        if not (alexa_client and alexa_client.unique_id):
            _LOGGER.debug("%s: Skipping creation of uninitialized device: %s",
                          account,
                          alexa_client)
            continue
        devices.append(alexa_client)
        (hass.data[DATA_ALEXAMEDIA]
         ['accounts']
         [account]
         ['entities']
         ['alarm_control_panel']) = alexa_client
    if devices:
        _LOGGER.debug("Adding %s", devices)
        try:
            add_devices_callback(devices, True)
        except HomeAssistantError as exception_:
            message = exception_.message  # type: str
            if message.startswith("Entity id already exists"):
                _LOGGER.debug("Device already added: %s",
                              message)
            else:
                _LOGGER.debug("Unable to add devices: %s : %s",
                              devices,
                              message)
    return True