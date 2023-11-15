def ipconfig_struct(config: IpConfig) -> dict:
    """Return a dict with information about ip configuration."""
    return {
        ATTR_METHOD: config.method,
        ATTR_ADDRESS: [address.with_prefixlen for address in config.address],
        ATTR_NAMESERVERS: [str(address) for address in config.nameservers],
        ATTR_GATEWAY: str(config.gateway) if config.gateway else None,
    }