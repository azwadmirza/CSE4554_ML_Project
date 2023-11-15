def interface_struct(interface: Interface) -> dict:
    """Return a dict with information of a interface to be used in th API."""
    return {
        ATTR_INTERFACE: interface.name,
        ATTR_TYPE: interface.type,
        ATTR_ENABLED: interface.enabled,
        ATTR_CONNECTED: interface.connected,
        ATTR_PRIMARY: interface.primary,
        ATTR_IPV4: ipconfig_struct(interface.ipv4) if interface.ipv4 else None,
        ATTR_IPV6: ipconfig_struct(interface.ipv6) if interface.ipv6 else None,
        ATTR_WIFI: wifi_struct(interface.wifi) if interface.wifi else None,
        ATTR_VLAN: wifi_struct(interface.vlan) if interface.vlan else None,
    }