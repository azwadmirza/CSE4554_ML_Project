def interface_ip(iface):
    '''
    Return the interface details
    '''
    return interfaces().get(iface, {}).get('inet', {})[0].get('address', {})