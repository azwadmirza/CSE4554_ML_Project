def accesspoint_struct(accesspoint: AccessPoint) -> dict:
    """Return a dict for AccessPoint."""
    return {
        ATTR_MODE: accesspoint.mode,
        ATTR_SSID: accesspoint.ssid,
        ATTR_FREQUENCY: accesspoint.frequency,
        ATTR_SIGNAL: accesspoint.signal,
        ATTR_MAC: accesspoint.mac,
    }