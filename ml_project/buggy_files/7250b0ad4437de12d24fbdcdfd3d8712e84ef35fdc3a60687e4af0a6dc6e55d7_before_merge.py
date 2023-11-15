async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up PS4 Platform."""
    creds = config.data[CONF_TOKEN]
    device_list = []
    for device in config.data["devices"]:
        host = device[CONF_HOST]
        region = device[CONF_REGION]
        name = device[CONF_NAME]
        ps4 = pyps4.Ps4Async(host, creds, device_name=DEFAULT_ALIAS)
        device_list.append(PS4Device(config, name, host, region, ps4, creds))
    async_add_entities(device_list, update_before_add=True)