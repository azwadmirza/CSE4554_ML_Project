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

    # On some distros (notably FreeBSD) if there is no hostname set
    # salt.utils.network.get_fqhostname() will return None.
    # In this case we punt and log a message at error level, but force the
    # hostname and domain to be localhost.localdomain
    # Otherwise we would stacktrace below
    if __FQDN__ is None:   # still!
        log.error('Having trouble getting a hostname.  Does this machine have its hostname and domain set properly?')
        __FQDN__ = 'localhost.localdomain'

    grains['fqdn'] = __FQDN__
    (grains['host'], grains['domain']) = grains['fqdn'].partition('.')[::2]
    return grains