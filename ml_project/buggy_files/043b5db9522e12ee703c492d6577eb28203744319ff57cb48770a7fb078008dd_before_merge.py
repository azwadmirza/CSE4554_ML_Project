def network_hosts(value, options=None, version=None):
    '''
    Return the list of hosts within a network.
    '''
    ipaddr_filter_out = _filter_ipaddr(value, options=options, version=version)
    if not ipaddr_filter_out:
        return
    if not isinstance(value, (list, tuple, types.GeneratorType)):
        return _network_hosts(ipaddr_filter_out[0])
    return [
        _network_hosts(ip_a)
        for ip_a in ipaddr_filter_out
    ]