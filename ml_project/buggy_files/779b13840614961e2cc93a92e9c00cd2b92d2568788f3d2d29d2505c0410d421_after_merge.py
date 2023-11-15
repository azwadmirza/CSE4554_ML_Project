def _grains():
    '''
    Get the grains from the proxied device.
    '''
    try:
        host = __pillar__['proxy']['host']
        if host:
            username, password = _find_credentials(host)
            protocol = __pillar__['proxy'].get('protocol')
            port = __pillar__['proxy'].get('port')
            ret = salt.modules.vsphere.system_info(host=host,
                                                   username=username,
                                                   password=password,
                                                   protocol=protocol,
                                                   port=port)
            GRAINS_CACHE.update(ret)
    except KeyError:
        pass

    return GRAINS_CACHE