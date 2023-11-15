def dns():
    '''
    Parse the resolver configuration file

     .. versionadded:: 2016.3.0
    '''
    # Provides:
    #   dns
    if salt.utils.is_windows() or 'proxyminion' in __opts__:
        return {}

    resolv = salt.utils.dns.parse_resolv()
    keys = ['nameservers', 'ip4_nameservers', 'sortlist']
    if __opts__.get('ipv6', True):
        keys.append('ip6_nameservers')
    for key in keys:
        if key in resolv:
            resolv[key] = [str(i) for i in resolv[key]]

    return {'dns': resolv} if resolv else {}