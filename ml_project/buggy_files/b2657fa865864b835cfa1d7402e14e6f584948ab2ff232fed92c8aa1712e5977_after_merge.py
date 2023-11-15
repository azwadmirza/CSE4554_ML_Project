async def async_setup_entry(hass, config_entry):
    """Set up TPLink from a config entry."""
    from pyHS100 import SmartBulb, SmartPlug, SmartDeviceException

    devices = {}

    config_data = hass.data[DOMAIN].get(ATTR_CONFIG)

    # These will contain the initialized devices
    lights = hass.data[DOMAIN][CONF_LIGHT] = []
    switches = hass.data[DOMAIN][CONF_SWITCH] = []

    # If discovery is defined and not disabled, discover devices
    # If initialized from configure integrations, there's no config
    # so we default here to True
    if config_data is None or config_data[CONF_DISCOVERY]:
        devs = await _async_has_devices(hass)
        _LOGGER.info("Discovered %s TP-Link smart home device(s)", len(devs))
        devices.update(devs)

    def _device_for_type(host, type_):
        dev = None
        if type_ == CONF_LIGHT:
            dev = SmartBulb(host)
        elif type_ == CONF_SWITCH:
            dev = SmartPlug(host)

        return dev

    # When arriving from configure integrations, we have no config data.
    if config_data is not None:
        for type_ in [CONF_LIGHT, CONF_SWITCH]:
            for entry in config_data[type_]:
                try:
                    host = entry['host']
                    dev = _device_for_type(host, type_)
                    devices[host] = dev
                    _LOGGER.debug("Succesfully added %s %s: %s",
                                  type_, host, dev)
                except SmartDeviceException as ex:
                    _LOGGER.error("Unable to initialize %s %s: %s",
                                  type_, host, ex)

    # This is necessary to avoid I/O blocking on is_dimmable
    def _fill_device_lists():
        for dev in devices.values():
            if isinstance(dev, SmartPlug):
                try:
                    if dev.is_dimmable:  # Dimmers act as lights
                        lights.append(dev)
                    else:
                        switches.append(dev)
                except SmartDeviceException as ex:
                    _LOGGER.error("Unable to connect to device %s: %s",
                                  dev.host, ex)

            elif isinstance(dev, SmartBulb):
                lights.append(dev)
            else:
                _LOGGER.error("Unknown smart device type: %s", type(dev))

    # Avoid blocking on is_dimmable
    await hass.async_add_executor_job(_fill_device_lists)

    forward_setup = hass.config_entries.async_forward_entry_setup
    if lights:
        _LOGGER.debug("Got %s lights: %s", len(lights), lights)
        hass.async_create_task(forward_setup(config_entry, 'light'))
    if switches:
        _LOGGER.debug("Got %s switches: %s", len(switches), switches)
        hass.async_create_task(forward_setup(config_entry, 'switch'))

    return True