def check_nova():
    if HAS_NOVA:
        novaclient_ver = LooseVersion(novaclient.__version__)
        min_ver = LooseVersion(NOVACLIENT_MINVER)
        if novaclient_ver >= min_ver:
            return HAS_NOVA
        log.debug('Newer novaclient version required.  Minimum: 2.6.1')
    return False