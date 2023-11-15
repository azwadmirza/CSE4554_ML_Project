def interface_ip(iface):
    '''
    Return the interface details
    '''
    try:
        return interfaces().get(iface, {}).get('inet', {})[0].get('address', {})
    except KeyError:
        return {}  # iface has no IP