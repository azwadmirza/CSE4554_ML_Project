def hostname():
    '''
    Return fqdn, hostname, domainname
    '''
    # This is going to need some work
    # Provides:
    #   fqdn
    #   host
    #   localhost
    #   domain
    global __FQDN__
    grains = {}

    if salt.utils.is_proxy():
        return grains

    grains['localhost'] = socket.gethostname()
    if __FQDN__ is None:
        __FQDN__ = salt.utils.network.get_fqhostname()
    grains['fqdn'] = __FQDN__
    (grains['host'], grains['domain']) = grains['fqdn'].partition('.')[::2]
    return grains