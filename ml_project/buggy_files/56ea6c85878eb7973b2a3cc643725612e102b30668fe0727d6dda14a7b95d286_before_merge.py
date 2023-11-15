def setup_platform(hass, config, add_devices_callback,
                   discovery_info=None):
    """Set up the Alexa alarm control panel platform."""
    devices = []  # type: List[AlexaAlarmControlPanel]
    for account, account_dict in (hass.data[DATA_ALEXAMEDIA]
                                  ['accounts'].items()):
        alexa_client = AlexaAlarmControlPanel(account_dict['login_obj'],
                                              hass)  \
                                              # type: AlexaAlarmControlPanel
        devices.append(alexa_client)
        (hass.data[DATA_ALEXAMEDIA]
         ['accounts']
         [account]
         ['entities']
         ['alarm_control_panel']) = alexa_client
    _LOGGER.debug("Adding %s", devices)
    add_devices_callback(devices, True)
    return True