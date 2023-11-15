async def async_setup_platform(
    hass, config, add_devices_callback, discovery_info=None
) -> bool:
    """Set up the Alexa alarm control panel platform."""
    devices = []  # type: List[AlexaAlarmControlPanel]
    account = config[CONF_EMAIL]
    include_filter = config.get(CONF_INCLUDE_DEVICES, [])
    exclude_filter = config.get(CONF_EXCLUDE_DEVICES, [])
    account_dict = hass.data[DATA_ALEXAMEDIA]["accounts"][account]
    guard_media_players = {}
    for key, device in account_dict["devices"]["media_player"].items():
        if key not in account_dict["entities"]["media_player"]:
            _LOGGER.debug(
                "%s: Media player %s not loaded yet; delaying load",
                hide_email(account),
                hide_serial(key),
            )
            raise ConfigEntryNotReady
        if "GUARD_EARCON" in device["capabilities"]:
            guard_media_players[key] = account_dict["entities"]["media_player"][key]
    if "alarm_control_panel" not in (account_dict["entities"]):
        (
            hass.data[DATA_ALEXAMEDIA]["accounts"][account]["entities"][
                "alarm_control_panel"
            ]
        ) = {}
    alexa_client: AlexaAlarmControlPanel = AlexaAlarmControlPanel(
        account_dict["login_obj"], guard_media_players
    )
    await alexa_client.init()
    if not (alexa_client and alexa_client.unique_id):
        _LOGGER.debug(
            "%s: Skipping creation of uninitialized device: %s",
            hide_email(account),
            alexa_client,
        )
    elif alexa_client.unique_id not in (
        account_dict["entities"]["alarm_control_panel"]
    ):
        devices.append(alexa_client)
        (
            hass.data[DATA_ALEXAMEDIA]["accounts"][account]["entities"][
                "alarm_control_panel"
            ][alexa_client.unique_id]
        ) = alexa_client
    else:
        _LOGGER.debug(
            "%s: Skipping already added device: %s", hide_email(account), alexa_client
        )
    return await add_devices(
        hide_email(account),
        devices,
        add_devices_callback,
        include_filter,
        exclude_filter,
    )