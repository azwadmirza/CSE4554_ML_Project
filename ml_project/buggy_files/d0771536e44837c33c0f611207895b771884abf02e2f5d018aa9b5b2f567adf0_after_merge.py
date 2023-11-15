def ip_to_host(ip):
    '''
    Returns the hostname of a given IP
    '''
    try:
        hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip)
    except Exception as exc:
        log.debug('salt.utils.network.ip_to_host(%r) failed: %s', ip, exc)
        hostname = None
    return hostname