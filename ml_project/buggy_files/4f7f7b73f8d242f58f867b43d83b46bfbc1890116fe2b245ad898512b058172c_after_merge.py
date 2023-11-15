async def async_setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Set up the Alexa sensor platform."""
    devices: List[AlexaMediaNotificationSensor] = []
    SENSOR_TYPES = {
        "Alarm": AlarmSensor,
        "Timer": TimerSensor,
        "Reminder": ReminderSensor,
    }
    account = config[CONF_EMAIL]
    include_filter = config.get(CONF_INCLUDE_DEVICES, [])
    exclude_filter = config.get(CONF_EXCLUDE_DEVICES, [])
    account_dict = hass.data[DATA_ALEXAMEDIA]["accounts"][account]
    _LOGGER.debug("%s: Loading sensors", hide_email(account))
    if "sensor" not in account_dict["entities"]:
        (hass.data[DATA_ALEXAMEDIA]["accounts"][account]["entities"]["sensor"]) = {}
    for key, device in account_dict["devices"]["media_player"].items():
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
        if key not in (account_dict["entities"]["sensor"]):
            (account_dict["entities"]["sensor"][key]) = {}
            for (n_type, class_) in SENSOR_TYPES.items():
                n_type_dict = (
                    account_dict["notifications"][key][n_type]
                    if key in account_dict["notifications"]
                    and n_type in account_dict["notifications"][key]
                    else {}
                )
                if (
                    n_type in ("Alarm, Timer")
                    and "TIMERS_AND_ALARMS" in device["capabilities"]
                ):
                    alexa_client = class_(
                        account_dict["entities"]["media_player"][key],
                        n_type_dict,
                        account,
                    )
                elif n_type in ("Reminder") and "REMINDERS" in device["capabilities"]:
                    alexa_client = class_(
                        account_dict["entities"]["media_player"][key],
                        n_type_dict,
                        account,
                    )
                else:
                    continue
                _LOGGER.debug(
                    "%s: Found %s %s sensor (%s) with next: %s",
                    hide_email(account),
                    hide_serial(key),
                    n_type,
                    len(n_type_dict.keys()),
                    alexa_client.state,
                )
                devices.append(alexa_client)
                (account_dict["entities"]["sensor"][key][n_type]) = alexa_client
        else:
            for alexa_client in account_dict["entities"]["sensor"][key].values():
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