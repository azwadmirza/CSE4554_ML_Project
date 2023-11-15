async def async_setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Set up the Alexa switch platform."""
    devices = []  # type: List[DNDSwitch]
    SWITCH_TYPES = [
        ("dnd", DNDSwitch),
        ("shuffle", ShuffleSwitch),
        ("repeat", RepeatSwitch),
    ]
    account = config[CONF_EMAIL]
    include_filter = config.get(CONF_INCLUDE_DEVICES, [])
    exclude_filter = config.get(CONF_EXCLUDE_DEVICES, [])
    account_dict = hass.data[DATA_ALEXAMEDIA]["accounts"][account]
    _LOGGER.debug("%s: Loading switches", hide_email(account))
    if "switch" not in account_dict["entities"]:
        (hass.data[DATA_ALEXAMEDIA]["accounts"][account]["entities"]["switch"]) = {}
    for key, _ in account_dict["devices"]["media_player"].items():
        if key not in account_dict["entities"]["media_player"]:
            _LOGGER.debug(
                "%s: Media player %s not loaded yet; delaying load",
                hide_email(account),
                hide_serial(key),
            )
            if devices:
                await add_devices(
                    hide_email(account),
                    devices,
                    add_devices_callback,
                    include_filter,
                    exclude_filter,
                )
            return False
        if key not in (
            hass.data[DATA_ALEXAMEDIA]["accounts"][account]["entities"]["switch"]
        ):
            (
                hass.data[DATA_ALEXAMEDIA]["accounts"][account]["entities"]["switch"][
                    key
                ]
            ) = {}
            for (switch_key, class_) in SWITCH_TYPES:
                if (
                    switch_key == "dnd"
                    and not account_dict["devices"]["switch"][key].get("dnd")
                ) or (
                    switch_key in ["shuffle", "repeat"]
                    and "MUSIC_SKILL"
                    not in account_dict["devices"]["media_player"][key].get(
                        "capabilities"
                    )
                ):
                    _LOGGER.debug(
                        "%s: Skipping %s for %s",
                        hide_email(account),
                        switch_key,
                        hide_serial(key),
                    )
                    continue
                alexa_client = class_(
                    account_dict["entities"]["media_player"][key], account
                )  # type: AlexaMediaSwitch
                _LOGGER.debug(
                    "%s: Found %s %s switch with status: %s",
                    hide_email(account),
                    hide_serial(key),
                    switch_key,
                    alexa_client.is_on,
                )
                devices.append(alexa_client)
                (
                    hass.data[DATA_ALEXAMEDIA]["accounts"][account]["entities"][
                        "switch"
                    ][key][switch_key]
                ) = alexa_client
        else:
            for alexa_client in hass.data[DATA_ALEXAMEDIA]["accounts"][account][
                "entities"
            ]["switch"][key].values():
                _LOGGER.debug(
                    "%s: Skipping already added device: %s",
                    hide_email(account),
                    alexa_client,
                )
    return await add_devices(
        hide_email(account),
        devices,
        add_devices_callback,
        include_filter,
        exclude_filter,
    )