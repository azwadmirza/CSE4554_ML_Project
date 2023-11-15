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
    for key in ('nameservers', 'ip4_nameservers', 'ip6_nameservers',
                'sortlist'):
        if key in resolv:
            resolv[key] = [str(i) for i in resolv[key]]

    return {'dns': resolv} if resolv else {}