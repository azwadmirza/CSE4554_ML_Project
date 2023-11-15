def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the HomeMatic switch platform."""
    if discovery_info is None:
        return

    devices = []
    for conf in discovery_info[ATTR_DISCOVER_DEVICES]:
        new_device = HMSwitch(conf)
        devices.append(new_device)

    add_entities(devices)