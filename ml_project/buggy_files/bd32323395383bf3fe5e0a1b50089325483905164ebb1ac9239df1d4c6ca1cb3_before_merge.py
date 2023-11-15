def wifi_struct(config: WifiConfig) -> dict:
    """Return a dict with information about wifi configuration."""
    return {
        ATTR_MODE: config.mode,
        ATTR_AUTH: config.auth,
        ATTR_SSID: config.ssid,
        ATTR_SIGNAL: config.signal,
    }