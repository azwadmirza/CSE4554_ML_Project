async def async_setup_entry(hass, config_entry):
    """Set up Alexa Media Player as config entry."""

    async def close_alexa_media(event=None) -> None:
        """Clean up Alexa connections."""
        _LOGGER.debug("Received shutdown request: %s", event)
        for email, _ in hass.data[DATA_ALEXAMEDIA]["accounts"].items():
            await close_connections(hass, email)

    hass.data.setdefault(DATA_ALEXAMEDIA, {"accounts": {}})
    from alexapy import AlexaLogin, __version__ as alexapy_version

    _LOGGER.info(STARTUP)
    _LOGGER.info("Loaded alexapy==%s", alexapy_version)
    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, close_alexa_media)
    account = config_entry.data
    email = account.get(CONF_EMAIL)
    password = account.get(CONF_PASSWORD)
    url = account.get(CONF_URL)
    hass.data[DATA_ALEXAMEDIA]["accounts"].setdefault(
        email,
        {
            "config_entry": config_entry,
            "setup_platform_callback": setup_platform_callback,
            "test_login_status": test_login_status,
            "devices": {"media_player": {}, "switch": {}},
            "entities": {"media_player": {}, "switch": {}},
            "excluded": {},
            "new_devices": True,
            "websocket_lastattempt": 0,
            "websocketerror": 0,
            "websocket_commands": {},
            "websocket_activity": {"serials": {}, "refreshed": {}},
            "websocket": None,
            "auth_info": None,
            "configurator": [],
        },
    )
    login = hass.data[DATA_ALEXAMEDIA]["accounts"][email].get(
        "login_obj",
        AlexaLogin(url, email, password, hass.config.path, account.get(CONF_DEBUG)),
    )
    await login.login_with_cookie()
    await test_login_status(hass, config_entry, login, setup_platform_callback)
    return True