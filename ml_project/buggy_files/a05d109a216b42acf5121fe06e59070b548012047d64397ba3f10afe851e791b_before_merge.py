def __virtual__():
    try:
        if salt.utils.platform.is_proxy() and __opts__['proxy']['proxytype'] == 'fx2':
            return __virtualname__
    except KeyError:
        pass
    return False