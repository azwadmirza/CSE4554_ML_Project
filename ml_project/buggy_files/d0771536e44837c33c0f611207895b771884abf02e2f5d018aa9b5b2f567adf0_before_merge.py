def ip_to_host(ip):
    '''
    Returns the hostname of a given IP
    '''
    try:
        hostname, aliaslist, ipaddrlist = socket.gethostbyaddr(ip)
    except Exception:
        hostname = None
    return hostname