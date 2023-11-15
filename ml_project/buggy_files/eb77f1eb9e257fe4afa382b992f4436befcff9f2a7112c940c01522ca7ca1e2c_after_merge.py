def setup_platform(hass, config, add_entities, discovery_info=None):
    """Perform the setup for Xiaomi devices."""
    devices = []
    for (_, gateway) in hass.data[PY_XIAOMI_GATEWAY].gateways.items():
        for device in gateway.devices['cover']:
            model = device['model']
            if model == 'curtain':
                devices.append(XiaomiGenericCover(device, "Curtain",
                                                  'status', gateway))
    add_entities(devices)