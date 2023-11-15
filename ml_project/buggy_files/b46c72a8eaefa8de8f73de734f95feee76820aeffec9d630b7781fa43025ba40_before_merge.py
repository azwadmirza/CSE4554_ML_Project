def ip6_interfaces():
    '''
    Provide a dict of the connected interfaces and their ip6 addresses
    The addresses will be passed as a list for each interface
    '''
    # Provides:
    #   ip_interfaces

    if salt.utils.is_proxy() or not __opts__.get('ipv6', True):
        return {}

    ret = {}
    ifaces = _get_interfaces()
    for face in ifaces:
        iface_ips = []
        for inet in ifaces[face].get('inet6', []):
            if 'address' in inet:
                iface_ips.append(inet['address'])
        for secondary in ifaces[face].get('secondary', []):
            if 'address' in secondary:
                iface_ips.append(secondary['address'])
        ret[face] = iface_ips
    return {'ip6_interfaces': ret}